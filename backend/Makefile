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
	if [ -d "$(VENV)/bin" ]; then \
		$(VENV)/bin/uvicorn t4cclient.__main__:app --reload; \
	else \
		$(VENV)/Scripts/uvicorn t4cclient.__main__:app --reload; \
	fi

install: 
	$(VENV)/bin/pip install -e ".[dev]"

dev: database app

cleanup:
	docker stop capella-collab-postgres
	docker rm capella-collab-postgres
