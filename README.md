# EduGraph Tools

Tool support for the [EduGraph Ontology](https://github.com/christian-bick/edugraph-ontology)

Live version of the web interface: https://www.edugraph.io/

# Development

We use Docker for setting up the development environment:

- No need to install a local development environment (Node, Python)
- You can use any code editor you want (make sure it uses .editorconfig)

## Prerequisites

[Latest version of Docker](https://docs.docker.com/engine/install/) installed on your machine.

## Credential Setup

#### Creating Credentials:

You need to provide your own credentials for GenAI tasks: At the moment, we are only using Gemini.

You can get a Gemini API key with a free usage tier [here](https://ai.google.dev/gemini-api/docs/api-key).

#### Configuring Credentials:

In ``apps/`` create a copy of ``.env.example`` and name it ``.env``.

Then add your Gemini API Key to the ``.env`` file:

```
GOOGLE_API_KEY=AIxu7A76...
```

The environment variables in the ``.env`` file are automatically used by the python apps. 

The ``.env`` file is excluded from git tracking to avoid accidental credential exposure.

## Docker Setup

With the credentials in place, this command is all you need for getting started with local development:
```
docker-compose watch
```

- [x] Builds a docker image for
  - the web interface from `web/`
  - the api application from `apps/`
- [x] Hosts two services (web & api)
  - listening on port 3000 (web)
  - listening on port 8080 (api)
- [x] Syncs source code files with the containers
  - hot-swapping code without refresh (web)
  - automatically restarting the server (api)
- [x] Rebuilds images when dependencies are updated in
  - package.json (web)
  - pyproject.toml (api)

#### More Helpful Commands:

`docker-compose watch web` Same as `watch` but only for the web server

`docker-compose watch api` Same as `watch` but only for the api server

`docker-compose up` Same as `watch` but without file sync

`docker-compose stop` Stops all running services

See the [docker-compose manual](https://docs.docker.com/reference/cli/docker/compose/) for an overview of all available 
commands.

## Manual Setup

If you cannot use Docker for some reason or want to make changes to the Docker setup then you
will want to make yourself familiar with the following development tools:

### Web Module

- [nvm](https://github.com/nvm-sh/nvm) and [npm](https://www.npmjs.com/) for runtime & package management
- [vite](https://vite.dev/) for hosting during development and building the production release

Example:
```
nvm install 22
npm install
vite --host
```

_Requires nvm to be installed already._

### Apps Module

- [pipx](https://github.com/pypa/pipx) and [poetry](https://python-poetry.org/) for runtime & package management
- [flask](https://flask.palletsprojects.com/en/stable/) for hosting the api during development
- [waitress](https://pypi.org/project/waitress/) for hosting the api in production

Example:
``` 
pipx install poetry
poetry install
flask --debug run --host=0.0.0.0 --port=8080
```
_Requires pipx to be installed already_<br>
_Requires copying [ontology files](https://github.com/christian-bick/edugraph-ontology/releases)
into ``apps/`` (automated in the docker setup)_


# Deployment

See Github actions in `.github/workflows/` for an example of an automated building and deployment process.

### Web Module

Run `vite build` from `web/` for building a production ready web app bundle.

Deploy on `Github Pages` `Gitlab Pages` `Netlify` `Heroku` `Google Firebase` `Azure Static Web Apps` ...

### Apps Module

Run ``docker build .``from ``apps/`` for building an optimized python container.

Deploy on `AWS ECS` `Google Cloud Run` `Azure Container Apps` `Kubernetes` ...