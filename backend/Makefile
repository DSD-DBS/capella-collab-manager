DB_PORT = 5432

database: 
	docker start capella-collab-postgres || \
	docker run -d \
		--name capella-collab-postgres \
		-p $(DB_PORT):5432 \
		-e POSTGRES_PASSWORD=dev \
		-e POSTGRES_USER=dev \
		-e POSTGRES_DB=dev \
		postgres

python: 
	uvicorn t4cclient.__main__:app --reload

dev: database python
	
cleanup: 
	docker stop capella-collab-postgres
	docker rm capella-collab-postgres