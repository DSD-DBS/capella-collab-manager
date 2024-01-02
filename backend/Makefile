# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

DB_PORT = 5432
DB_PASSWORD = dev
DB_USER = dev
DB_NAME = dev
VENV = .venv

DATABASE_LOAD_FILE ?= ../local/load.sql
DATABASE_SAVE_DIR ?= ../local

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -euo pipefail -c

export MSYS_NO_PATHCONV=1
export DISABLE_SESSION_TIMEOUT ?= 1
export DISABLE_SESSION_COLLECTOR ?= 1
export DEVELOPMENT_MODE ?= 1

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
	if [ -d "$(VENV)/bin" ]; then
		source $(VENV)/bin/activate;
	else
		source $(VENV)/Scripts/activate;
	fi
	export OAUTHLIB_INSECURE_TRANSPORT=1;
	uvicorn --reload --reload-dir $$(pwd) --reload-include "*.py" --reload-include "*.yaml" --reload-include "*.yml" capellacollab.__main__:app

coverage:
	pytest \
		--cov-report term \
		--cov-report html \
		tests/

install:
	python generate_git_archival.py
	$(VENV)/bin/pip install -e ".[dev]"

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
	cat $(DATABASE_LOAD_FILE) | docker run -i -e PGPASSWORD=$(DB_PASSWORD) --network host --entrypoint="psql" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME)

save:
	docker run -i -e PGPASSWORD=$(DB_PASSWORD) --network host --entrypoint="pg_dump" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME) > $(DATABASE_SAVE_DIR)/$(shell date +"%FT%T").sql
