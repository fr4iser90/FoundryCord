#!/usr/bin/env bash

# =======================================================
# HomeLab Discord Bot - Database Functions
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
    
    # Create backup directory if it doesn't exist
    run_remote_command "mkdir -p ${DB_BACKUP_DIR}"
    
    # Get timestamp for backup name
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_name="homelab_backup_${timestamp}.sql"
    
    print_info "Creating database backup: ${backup_name}"
    run_remote_command "docker exec ${POSTGRES_CONTAINER} pg_dump -U postgres -d homelab > ${DB_BACKUP_DIR}/${backup_name}"
    
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
    
    # List available backups
    print_info "Available backups on server:"
    local available_backups=$(run_remote_command "ls -lh ${DB_BACKUP_DIR}/*.sql 2>/dev/null || echo 'No backups found'")
    
    local backup_file=""
    
    if [[ "$available_backups" == *"No backups found"* ]]; then
        # Check for local backups
        if [ -d "./backups" ] && [ "$(ls -A ./backups 2>/dev/null)" ]; then
            print_info "Local backups found:"
            ls -lh ./backups/*.sql
            
            # Ask user if they want to upload a local backup
            if get_yes_no "Would you like to upload a local backup to the server?"; then
                # List local backups
                local local_backups=$(ls -1 ./backups/*.sql 2>/dev/null)
                
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
    
    # Stop the bot to release database connections
    run_remote_command "cd ${DOCKER_DIR} && docker compose stop bot"
    
    # Restore the database
    run_remote_command "docker exec ${POSTGRES_CONTAINER} psql -U postgres -c 'DROP DATABASE IF EXISTS homelab WITH (FORCE)'"
    run_remote_command "docker exec ${POSTGRES_CONTAINER} psql -U postgres -c 'CREATE DATABASE homelab'"
    run_remote_command "docker exec ${POSTGRES_CONTAINER} psql -U postgres -d homelab -f /docker-entrypoint-initdb.d/${backup_file}"
    
    # Restart the bot
    run_remote_command "cd ${DOCKER_DIR} && docker compose start bot"
    
    print_success "Database restored successfully!"
    return 0
} 