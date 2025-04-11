{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    # Test dependencies
    pytest
    pytest-asyncio
    pytest-cov
    pytest-mock
    
    # Database dependencies
    sqlalchemy
    asyncpg
    alembic
    psycopg2
    
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
    echo "Python development environment activated"
    echo "PYTHONPATH set to: $PYTHONPATH"
    echo "Available commands:"
    echo "  pytest - Run tests"
    echo "  pytest -v - Run tests with verbose output"
    echo "  pytest --cov=app - Run tests with coverage report"
  '';
} 