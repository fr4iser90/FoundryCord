#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

def run_tests_on_server(server_user, server_host, server_dir):
    """Run pytest on the server"""
    print(f"Running tests on {server_user}@{server_host}:{server_dir}")
    
    # Command to run tests on the server
    cmd = f"ssh {server_user}@{server_host} 'cd {server_dir} && docker exec homelab-discord-bot pytest -xvs app/bot/tests/'"
    
    # Execute the command
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    # Print output
    print(stdout.decode())
    if stderr:
        print("Errors:", stderr.decode())
    
    # Return exit code
    return process.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run pytest on the server")
    parser.add_argument("--user", default="docker", help="SSH username")
    parser.add_argument("--host", default="192.168.178.33", help="Server hostname or IP")
    parser.add_argument("--dir", default="/home/docker/docker/companion-management/homelab-discord-bot", help="Project directory on server")
    
    args = parser.parse_args()
    
    exit_code = run_tests_on_server(args.user, args.host, args.dir)
    sys.exit(exit_code)