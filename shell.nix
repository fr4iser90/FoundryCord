{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    # Test dependencies
    pytest
    pytest-asyncio
    pytest-cov
    pytest-mock
    
    # Core Bot Dependency
    nextcord
    
    # Monitoring Dependency
    psutil

    # Database dependencies
    sqlalchemy
    asyncpg
    alembic
    psycopg2
    
    # Other dependencies
    python-dotenv
    py-cpuinfo
    speedtest-cli
    
    # Web dependencies
    fastapi
    
    # Security dependencies
    cryptography
    pyjwt
    
    # Development tools
    black
    mypy
    pylint
  ]);
in
pkgs.mkShell {
  buildInputs = [
    pythonEnv
    pkgs.tree
  ];
  
  shellHook = ''
    # Set PYTHONPATH to include the project root
    export PYTHONPATH="$PWD:$PYTHONPATH"
    
    # Alias for running tests inside the test Docker container
    alias pytest-docker='docker compose -f docker/test/docker-compose.yml run --rm test pytest "$@"'
    alias clean_py='sudo find . -type d -name '__pycache__' -exec rm -rf {} + && sudo find . -type d -name '.pytest_cache' -exec rm -rf {} +'
    alias db_upgrade='docker exec -it foundrycord-bot /bin/sh -c "alembic -c /app/shared/infrastructure/database/migrations/alembic/alembic.ini upgrade head"'
    
    # --- Function to update a single tree file ---
    _update_tree_file() {
      local target_dir="$1"
      local output_file="$2"
      # Exclude common irrelevant directories/files
      local exclude_pattern='__pycache__|.git|.idea|.vscode|.cursor|node_modules|.pytest_cache' 

      echo "Updating tree in $output_file for directory $target_dir..."
      # Overwrite file with header
      echo '```tree' > "$output_file"
      # Append tree output, excluding patterns
      tree -I "$exclude_pattern" "$target_dir" >> "$output_file"
      # Append footer
      echo '```' >> "$output_file"
      echo "Done updating $output_file."
    }

    # --- Alias to update all structure files ---
    alias update-trees='_update_tree_file app/web docs/3_developer_guides/02_architecture/web_structure.md && _update_tree_file app/tests docs/3_developer_guides/02_architecture/tests_structure.md && _update_tree_file app/shared docs/3_developer_guides/02_architecture/shared_structure.md && _update_tree_file app/bot docs/3_developer_guides/02_architecture/bot_structure.md'
    
    echo "Python development environment activated"
    echo "PYTHONPATH set to: $PYTHONPATH"
    echo "Available commands:"
    echo "  pytest - Run tests locally (might differ from CI/test env)"
    echo "  pytest-docker - Run tests inside the Docker test environment (recommended)"
    echo "     -> Example: pytest-docker tests/unit/bot/" 
    echo "  pytest --cov=app - Run local tests with coverage report"
    echo "  update-trees - Update structure markdown files (web, tests, shared, bot)"
  '';
} 