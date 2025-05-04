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
  ];
  
  shellHook = ''
    # Set PYTHONPATH to include the project root
    export PYTHONPATH="$PWD:$PYTHONPATH"
    
    # Alias for running tests inside the test Docker container
    alias pytest-docker='docker compose -f docker/test/docker-compose.yml run --rm test pytest "$@"'
    alias clean_py='sudo find . -type d -name '__pycache__' -exec rm -rf {} + && sudo find . -type d -name '.pytest_cache' -exec rm -rf {} +'
    
    echo "Python development environment activated"
    echo "PYTHONPATH set to: $PYTHONPATH"
    echo "Available commands:"
    echo "  pytest - Run tests locally (might differ from CI/test env)"
    echo "  pytest-docker - Run tests inside the Docker test environment (recommended)"
    echo "     -> Example: pytest-docker tests/unit/bot/" 
    echo "  pytest --cov=app - Run local tests with coverage report"
  '';
} 