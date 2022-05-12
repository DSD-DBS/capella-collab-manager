DB_PORT = 5432
DB_PASSWORD = dev
DB_USER = dev
DB_NAME = dev
VENV = .venv

database:
	docker start capella-collab-postgres || \
	docker run -d \
		--name capella-collab-postgres \
		-p $(DB_PORT):5432 \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_DB=$(DB_NAME) \
		postgres

app:
	export MSYS_NO_PATHCONV=1; \
	export OAUTHLIB_INSECURE_TRANSPORT=1; \
	export UVICORN_COMMAND="uvicorn --reload --reload-include "*.py" --reload-include "*.yaml" --reload-include "*.yml" t4cclient.__main__:app"; \
	if [ -d "$(VENV)/bin" ]; then \
		$(VENV)/bin/$${UVICORN_COMMAND}; \
	else \
		$(VENV)/Scripts/$${UVICORN_COMMAND}; \
	fi

dev: database app

cleanup:
	docker stop capella-collab-postgres
	docker rm capella-collab-postgres

dump: 
	docker run -e PGPASSWORD=$(DB_PASSWORD) --entrypoint pg_dump --network host postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME) > $$(pwd)/../local/tmp.sql

psql: 
	docker run -e PGPASSWORD=$(DB_PASSWORD) -it --network host --entrypoint="psql" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME)

clear: 
	echo "DROP DATABASE $(DB_NAME); CREATE DATABASE $(DB_NAME);" | docker run -e PGPASSWORD=$(DB_PASSWORD) -i --network host --entrypoint="psql" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' postgres

load: clear
	cat $$(pwd)/../local/load.sql | docker run -i -e PGPASSWORD=$(DB_PASSWORD) --network host --entrypoint="psql" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME)