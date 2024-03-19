import json
import os
import subprocess
from datetime import datetime

import flask
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

app = flask.Flask(__name__)
app_root_dir = os.path.dirname(os.path.abspath(__file__))

env_filename = f"{app_root_dir}/env.json"

# read config
try:
    with open(env_filename, 'r') as file:
        envs = json.load(file)
except json.JSONDecodeError as ex:
    print("env.json format is invalid: ", ex)
    exit(1)
except FileNotFoundError:
    envs = {}

# print(envs)

g_auth = HTTPBasicAuth()

users = envs.get("users", {})


@g_auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@app.route('/')
@g_auth.login_required
def index():
    user = HTTPBasicAuth().current_user()
    return flask.render_template('index.html.jinja', tasks=envs.get("tasks", {}), user=user)


@app.route('/call-task', methods=['POST'])
@g_auth.login_required
def call_task():
    user = HTTPBasicAuth().current_user()

    task_name = flask.request.form["task"]
    task = envs.get("tasks", {}).get(task_name, {})
    data = {"task_name": task_name, "command_process": []}

    authed_users = task.get("users", [])
    if '*' not in authed_users and user not in authed_users:
        data['error'] = "Not Authorized"
        return flask.render_template('task-process.html.jinja', data=data)

    commands = envs.get("tasks", {}).get(task_name, {}).get("commands", [])  # Add your commands here
    for command in commands:
        command_process = {
            "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "command": command,
        }

        output = ''
        error_output = ''
        try:
            command_parts = command.split()
            if command_parts[0] == 'cd':
                #
                # handle 'cd' command,
                #
                # the 'cd' command invoked by subprocess.Popen() can't change current working directory
                # for subsequent command, so use os.chdir() instead
                #
                os.chdir(command_parts[1])
                cwd = os.getcwd()
                output += f'Current directory is {cwd}\n'
                if os.path.realpath(command_parts[1]) != cwd:
                    raise Exception(f'Failed to change current directory')
                    # error_output += f'Failed to change current directory'

            else:
                #
                # handle other(except 'cd') commands
                #
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           shell=True)
                result, error = process.communicate()

                if result:
                    output += result.decode('utf-8')
                if error:
                    error_output += error.decode('utf-8')

            command_process['output'] = output
            command_process['error_output'] = error_output
            data['command_process'].append(command_process)
        except Exception as e:
            error_output += str(e) + '\n'

            command_process['output'] = output
            command_process['error_output'] = error_output
            data['command_process'].append(command_process)
            break

    return flask.render_template('task-process.html.jinja', data=data)


if __name__ == '__main__':
    port = envs.get('port', 44300)
    app.run(ssl_context='adhoc', host='0.0.0.0', port=port)
    # app.run(host='0.0.0.0', port=port)
