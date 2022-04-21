DB_PORT = 5432
VENV = .venv39/bin

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
	export REQUESTS_CA_BUNDLE=$$(pwd)/../certs/localhost.crt; \
	$(VENV)/uvicorn t4cclient.__main__:app --reload

dev: database app
	
cleanup: 
	docker stop capella-collab-postgres
	docker rm capella-collab-postgres