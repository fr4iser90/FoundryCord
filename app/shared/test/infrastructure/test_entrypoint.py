#!/usr/bin/env python3
"""
Test container entrypoint script.
Handles initialization and execution of test suites in Docker environment.
"""
import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

def setup_environment():
    """Prepare the test environment"""
    print("Setting up test environment...")
    
    # Ensure temp directory exists and has correct permissions
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp', mode=0o777)
    else:
        os.chmod('/tmp', 0o777)
    
    # Set environment variables
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['TESTING'] = 'True'
    os.environ['PYTEST_DOCKER'] = 'True'
    
    # Create results directory
    results_dir = '/app/tests/test-results'
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

def run_tests(test_path=None, extra_args=None):
    """Run pytest with specified arguments"""
    # Base pytest command
    cmd = [sys.executable, '-m', 'pytest', '-v']
    
    # Add test path if specified
    if test_path:
        cmd.append(test_path)
    
    # Add any extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    print(f"Running tests with command: {' '.join(cmd)}")
    
    # Execute pytest
    return subprocess.call(cmd)

def wait_for_commands():
    """Keep the container alive to receive commands"""
    print("Container is running in wait mode. Use 'docker exec' to run commands.")
    try:
        while True:
            time.sleep(3600)  # Sleep for an hour at a time
    except KeyboardInterrupt:
        print("Container stopping due to interrupt")

def main():
    """Main entrypoint function"""
    parser = argparse.ArgumentParser(description='Test container entrypoint')
    parser.add_argument('--test', help='Run tests with optional path')
    parser.add_argument('--wait', action='store_true', help='Keep container running')
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--functional', action='store_true', help='Run functional tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    
    args, unknown = parser.parse_known_args()
    
    # Setup the environment regardless of command
    setup_environment()
    
    # Run the appropriate command
    if args.test:
        return run_tests(args.test, unknown)
    elif args.unit:
        return run_tests('app/tests/unit/', unknown)
    elif args.integration:
        return run_tests('app/tests/integration/', unknown)
    elif args.functional:
        return run_tests('app/tests/functional/', unknown)
    elif args.performance:
        return run_tests('app/tests/performance/', unknown)
    elif args.wait or not any(vars(args).values()):
        # Default to wait mode if no arguments or --wait is specified
        wait_for_commands()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())