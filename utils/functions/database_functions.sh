#!/usr/bin/env bash

# =======================================================
# Database Functions
# =======================================================

# Run Alembic migration
run_alembic_migration() {
    clear
    print_section_header "Alembic Migration"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot apply migration in local mode"
        return 1
    fi
    
    ./utils/database/update_alembic_migration.sh
    return $?
}

# Update remote database
update_remote_database() {
    clear
    print_section_header "Update Remote Database"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot update database in local mode"
        return 1
    fi
    
    ./utils/database/update_remote_database.sh
    return $?
}

# Backup database
backup_database() {
    show_header
    print_section_header "Database Backup"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot backup database in local mode"
        return 1
    fi
    
    # Use DB_BACKUP_DIR from config (ensure it's set in project_config if needed)
    export DB_BACKUP_DIR="${DB_BACKUP_DIR:-${EFFECTIVE_PROJECT_DIR}/backups}"
    run_remote_command "mkdir -p ${DB_BACKUP_DIR}"
    
    # Get timestamp for backup name using PROJECT_NAME and DB_NAME
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_name="${PROJECT_NAME}_${DB_NAME}_backup_${timestamp}.sql"
    
    print_info "Creating database backup: ${backup_name}"
    # Use DB_CONTAINER_NAME and DB_NAME variables
    run_remote_command "docker exec ${DB_CONTAINER_NAME} pg_dump -U postgres -d ${DB_NAME} > ${DB_BACKUP_DIR}/${backup_name}"
    
    # Ask if user wants to download backup
    if get_yes_no "Do you want to download the backup to your local machine?"; then
        # Create local backup directory if it doesn't exist
        mkdir -p "./backups"
        
        # Download the backup
        print_info "Downloading backup..."
        scp "${SERVER_USER}@${SERVER_HOST}:${DB_BACKUP_DIR}/${backup_name}" "./backups/"
        
        if [ $? -eq 0 ]; then
            print_success "Backup downloaded successfully to ./backups/${backup_name}"
        else
            print_error "Failed to download backup"
        fi
    fi
    
    print_success "Database backup completed!"
    return 0
}

# Restore database
restore_database() {
    show_header
    print_section_header "Database Restore"
    
    if [ "$RUN_LOCALLY" = true ]; then
        print_error "Cannot restore database in local mode"
        return 1
    fi
    
    # Use DB_BACKUP_DIR from config (ensure it's set in project_config if needed)
    export DB_BACKUP_DIR="${DB_BACKUP_DIR:-${EFFECTIVE_PROJECT_DIR}/backups}"

    # List available backups
    print_info "Available backups on server:"
    local available_backups=$(run_remote_command "ls -lh ${DB_BACKUP_DIR}/${PROJECT_NAME}_${DB_NAME}_backup_*.sql 2>/dev/null || echo 'No backups found'") # Filter by expected name pattern
    
    local backup_file=""
    
    if [[ "$available_backups" == *"No backups found"* ]]; then
        # Check for local backups
        if [ -d "./backups" ] && [ "$(ls -A ./backups 2>/dev/null)" ]; then
            print_info "Local backups found:"
            ls -lh ./backups/*.sql
            
            # Ask user if they want to upload a local backup
            if get_yes_no "Would you like to upload a local backup to the server?"; then
                # List local backups
                local local_backups=$(ls -1 ./backups/${PROJECT_NAME}_${DB_NAME}_backup_*.sql 2>/dev/null)
                
                # Ask which backup to upload
                print_info "Available local backups:"
                ls -lh ./backups/*.sql
                read -p "Enter the name of the backup file to upload: " local_backup
                
                if [ -f "./backups/${local_backup}" ]; then
                    # Upload backup
                    print_info "Uploading backup..."
                    scp "./backups/${local_backup}" "${SERVER_USER}@${SERVER_HOST}:${DB_BACKUP_DIR}/"
                    
                    if [ $? -eq 0 ]; then
                        print_success "Backup uploaded successfully"
                        backup_file="${local_backup}"
                    else
                        print_error "Failed to upload backup file"
                        return 1
                    fi
                else
                    print_error "Local backup file not found"
                    return 1
                fi
            else
                return 0
            fi
        else
            print_error "No local backups found in ./backups/ directory"
            return 1
        fi
    else
        echo "$available_backups"
        
        read -p "Enter the name of the backup file to restore: " backup_file
        
        if ! run_remote_command "test -f ${DB_BACKUP_DIR}/${backup_file}" "true"; then
            print_error "Backup file not found"
            return 1
        fi
    fi
    
    # Ask for confirmation
    if ! get_confirmed_input "⚠️ This will overwrite the current database. Are you sure?" "yes"; then
        print_info "Restore cancelled"
        return 0
    fi
    
    print_info "Restoring database from ${backup_file}..."
    
    # Restore the database using DB_CONTAINER_NAME and DB_NAME
    # Stop relevant containers first (maybe MAIN_CONTAINER or others dependent on DB?)
    # This needs careful consideration based on the actual stack dependencies
    # For now, let's assume stopping MAIN_CONTAINER is sufficient, but this might need adjustment
    print_warning "Stopping main container (${MAIN_CONTAINER}) before restore..."
    run_remote_command "cd ${EFFECTIVE_DOCKER_DIR} && ${DOCKER_COMPOSE_CMD} stop ${MAIN_CONTAINER}"
    
    run_remote_command "docker exec ${DB_CONTAINER_NAME} psql -U postgres -c 'DROP DATABASE IF EXISTS ${DB_NAME} WITH (FORCE)'"
    run_remote_command "docker exec ${DB_CONTAINER_NAME} psql -U postgres -c 'CREATE DATABASE ${DB_NAME}'"
    run_remote_command "docker exec ${DB_CONTAINER_NAME} psql -U postgres -d ${DB_NAME} -f /docker-entrypoint-initdb.d/${backup_file}"
    
    # Restart the main container
    print_info "Restarting main container (${MAIN_CONTAINER})..."
    run_remote_command "cd ${EFFECTIVE_DOCKER_DIR} && ${DOCKER_COMPOSE_CMD} start ${MAIN_CONTAINER}"
    
    print_success "Database restored successfully!"
    return 0
} 