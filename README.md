# Explorer

This repository contains explorer built for Rapids from scratch.

## Installation guide

0) Set up and configure Rapids node. 

1) Create virtual enviroment and install dependencies from [requirements.txt](requirements.txt) file.

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

2) Copy example config from [docs](docs/) folder and fill proper details.

3) Set up systemd services using example explorer and sync services from [docs](docs/) folder ([tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)).

4) Enjoy :)

Made with ❤️ by [Volbil](https://github.com/volbil)
