import argparse
import json
import os
from datetime import datetime

from werkzeug.security import generate_password_hash


def write_user_info(username, password):
    env_filename = 'env.json'

    # Read existing user info from JSON file
    try:
        with open(env_filename, 'r') as file:
            envs = json.load(file)
    except FileNotFoundError:
        envs = {}

    # print(envs)

    # Check if username exists in the existing user info
    if username not in envs["users"]:
        # Add new user info to existing user info
        envs["users"][username] = generate_password_hash(password)

        # Backup the old JSON file with timestamp added to filename
        backup_filename = None
        if os.path.exists(env_filename):
            backup_filename = f"env_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
            os.rename(env_filename, backup_filename)

        # Write updated user info to JSON file
        with open(env_filename, 'w') as file:
            json.dump(envs, file, indent=2)
        print(f"User {username} has been added.")
        if backup_filename:
            print(f"Old env is backed up as {backup_filename}.")
    else:
        print(f"Username {username} already exists.")


if __name__ == '__main__':
    # Create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', type=str, help='Username')
    parser.add_argument('--password', type=str, help='Password')
    args = parser.parse_args()

    # Call write_user_info function with provided username and password
    if args.username and args.password:
        write_user_info(args.username, args.password)
    else:
        print("Please provide both --username and --password options.")
