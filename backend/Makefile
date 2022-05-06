DB_PORT = 5432
VENV = .venv

database:
	docker start capella-collab-postgres || \
	docker run -d \
		--name capella-collab-postgres \
		-p $(DB_PORT):5432 \
		-e POSTGRES_PASSWORD=dev \
		-e POSTGRES_USER=dev \
		-e POSTGRES_DB=dev \
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
