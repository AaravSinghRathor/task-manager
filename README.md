## Deployment guidelines

### Pre-requiste
- Docker (view https://docs.docker.com/engine/install/)

## How to deploy?

- Create `.env` in base directory based on `.env-example`
- Execute `docker compose up --build`

---------------------------
## Development setup

### Pre-requiste
- Python 3.11
- Poetry

### Guidelines
- Each microservice has separate requirements. Hence, it is advisable to open each of them as separate entities.
- Create virtual env

  `python3 -m venv env`
- Install dependencies

  `poetry install`
- Your dev environment should be ready for development!

- To run the service:
1. Load env variables `source .env`
2. Execute:

    `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000`

3. You can use uvicorn also if you do not need the multiple workers

   `uvicorn your_module_name:app --host 0.0.0.0 --port 8000 --reload`


### API Docs:

- API docs can be viewed on `/docs` endpoint on their respective services.