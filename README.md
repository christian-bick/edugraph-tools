# EduGraph Tools

Tool support for the [EduGraph Ontology](https://github.com/christian-bick/edugraph-ontology)

Live version of the web interface: https://www.edugraph.io/

## Development

We use Docker for setting up the development environment:

- No need to install a local development environment (Node, Python)
- You can use any code editor you want (make sure it uses .editorconfig)

### Prerequisites

[Latest version of Docker](https://docs.docker.com/engine/install/) installed on your machine

### Credential Setup

Before starting, we need to set up our private credentials for GenAI tasks.

At the moment, we are only using Gemini for that purpose. You can get a Gemini API key with a free usage tier
[here](https://ai.google.dev/gemini-api/docs/api-key).

**After cloning the repository:**

In ``apps/`` make a copy of ``.env.example`` and name it ``.env``.

Then add your Gemini API Key to the ``.env`` file:

```
API_KEY_GEMINI=AIxu7A76...
```

The environment variables in the ``.env`` file are automatically used by the python apps. 

The ``.env`` file is excluded from git tracking to avoid accidental credential exposure.

### Docker Setup

```
docker-compose watch
```

1. Builds a docker image for

- a web interface (web)
- a data application using the latest ontology version (apps)

2. Hosts two web interfaces

- listening on port 3000 (web)
- listening on port 8080 (apps)

3. Syncs source code files with the containers

- hot-swapping code without refresh (web)
- automatically restarting the api (apps)

4. Rebuilds images when dependencies are updated in

- package.json (web)
- pyproject.toml (apps)

**This is all you should need for getting started with local development.**

### Manual Setup

If you cannot use Docker for some reason or want to make changes to the Docker setup then you
will want to make yourself familiar with the following development tools:

#### Web module

- [nvm](https://github.com/nvm-sh/nvm) and [npm](https://www.npmjs.com/) for runtime & package management
- [vite](https://vite.dev/) for hosting during development and building the production release

**Example:**

```
nvm install 22
npm install
vite --host
```

Requires _nvm_ to be installed already.

### Apps module

- [pipx](https://github.com/pypa/pipx) and [poetry](https://python-poetry.org/) for runtime & package management
- [flask](https://flask.palletsprojects.com/en/stable/) for hosting the api during development
- [waitress](https://pypi.org/project/waitress/) for hosting the api in production

**Example:**

```
pipx install poetry
poetry install
flask --debug run --host=0.0.0.0 --port=8080
```

Requires _pipx_ to be installed already.

Requires _copying the files_ from [ontology releases](https://github.com/christian-bick/edugraph-ontology/releases)
into the _apps_ root folder (automated in the docker setup).

## Deployment

See Github actions ``.github/workflows/`` for an example of an automated building and deployment process.

#### Web App

Run ``vite build`` from ``web/`` for building a production ready web app bundle.

Deploy on ``Github Pages, Gitlab Pages, Netlify, Heroku, Google Firebase, Azure Static Web Apps`` ...

#### API App

Run ``docker build .``from ``apps/`` for building an optimized python container.

Deploy on ``AWS ECS, Google Cloud Run, Azure Container Apps, Kubernetes`` ...