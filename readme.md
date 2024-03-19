

<!-- toc -->

- [Introduction](#introduction)
- [Installing](#installing)
  * [Installing Python](#installing-python)
  * [Activate the virtual python environment](#activate-the-virtual-python-environment)
  * [Install dependent packages](#install-dependent-packages)
- [Usage](#usage)
  * [Running](#running)
  * [Access from a browser](#access-from-a-browser)
  * [Running at boot time in background](#running-at-boot-time-in-background)
- [Configuration File](#configuration-file)
  * [Adding a user](#adding-a-user)
  * [Removing a user](#removing-a-user)
  * [Adding a task](#adding-a-task)

<!-- tocstop -->

## Introduction

This tool can let you call a predefined list of commands on your server from a browser in relatively safe way

## Installing

### Installing Python

Please follow this link to install Python(>=3.9): https://www.python.org/downloads/

Install and activate a virtual python environment
```
cd /your/webrun

# install virtual python environment
python -m venv .venv
```

### Activate the virtual python environment

```
cd /your/webrun
source .venv/bin/activate
```

> Please make sure you have activated the virtual environment before running any command in this manual

Confirm the python path

`which python`

It should show the path like this: `/your/webrun/.venv/bin/python ...`

### Install dependent packages

```
pip install -r requirements.txt
```

## Usage

### Running

Method 1, Use flask development server:

```
python start.py
```

> the command will show the web address which can be accessed from your browser

Method 2, Use `gunicorn` which is recommended for production environment by flask document:

```
# generate self-signed ssl certification
openssl genrsa -out cert/server.key 2048
openssl req -new -key cert/server.key -out cert/server.csr
openssl x509 -req -days 3650 -in cert/server.csr -signkey cert/server.key -out cert/server.crt

# start service
gunicorn -b 0.0.0.0:44300 --keyfile /your/webrun/cert/server.key --certfile /your/webrun/cert/server.crt start:app
```

### Access from a browser

It can be accessed from a browser by address: **https://your-server:44300**

> The browser would show a warning `Your connection is not private` due to the service uses a self-signed SSL certificate by default for https connection.
> You can apply a formal certificate (eg: apply from [Let's Encrypt](https://letsencrypt.org)) to eliminate the warning.

### Running at boot time in background

It can be run as a background service by `supervisord`:
[http://supervisord.org](http://supervisord.org)

Just make sure the command which will be added into configuration of `supervisord` as the following:
 
```
/your/webrun/.venv/bin/python /your/webrun/start.py
```
or
```
/your/webrun/.venv/bin/gunicorn -b 0.0.0.0:44300 --keyfile /your/webrun/cert/server.key --certfile /your/webrun/cert/server.crt start:app
```

## Configuration File

Configuration file `env.json` should be in the root directory. 

`env.sample.json` is an example of `env.json`

> the service have to be restarted to make the updated configuration file take effect after the `env.json` is updated


### Adding a user

```
python new_user.py --username=spiderman --password=...
```

> The user and the encrypted password would be saved into `env.json` configuration file 

### Removing a user

Edit the `env.json` configuration file and remove a user from the root `users`

```
{
  "users": {
    "spiderman": "...",    # removing this line will remove the user 
    "hulk": "...",
    ...
  }
  "tasks": {
    ...
  }
}
```

### Adding a task

Edit the `env.json` file and add a task `pull-code`:

```
{
  "users": {
    "spiderman": "..."
  }
  "tasks": {
    "pull-code": {
      "users": [         # no users means no one allowed
        "spiderman",     # authed user name
        "*"              # allowing all logged in user
      ],
      "commands": [
        "cd /your/project",
        "git pull origin main"
      ]
    }
  }
}
```

