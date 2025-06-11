# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

DB_PORT = 5432
DB_PASSWORD = dev
DB_USER = dev
DB_NAME = dev

VALKEY_PASSWORD ?= password

VENV = .venv

export HOST ?= 127.0.0.1

VALKEY_PORT = 6379

DATABASE_LOAD_FILE ?= ../local/load.sql
DATABASE_SAVE_DIR ?= ../local

.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS = -euo pipefail -c

export MSYS_NO_PATHCONV=1
export DISABLE_SESSION_TIMEOUT ?= 1
export DISABLE_SESSION_COLLECTOR ?= 1
export LOCAL_DEVELOPMENT_MODE ?= 1
export FASTAPI_AUTO_RELOAD ?= 1

database:
	docker start capella-collab-postgres || \
	docker run -d \
		--name capella-collab-postgres \
		-p $(DB_PORT):5432 \
		-e POSTGRES_PASSWORD=$(DB_PASSWORD) \
		-e POSTGRES_USER=$(DB_USER) \
		-e POSTGRES_DB=$(DB_NAME) \
		postgres

valkey:
	TMP_FILE=$$(mktemp)
	echo "requirepass $(VALKEY_PASSWORD)" > $$TMP_FILE
	docker start capella-collab-valkey || \
	docker run -d \
		--name capella-collab-valkey \
		--rm \
		-p $(VALKEY_PORT):6379 \
		-v $$TMP_FILE:/usr/local/etc/valkey/valkey.conf \
		valkey/valkey:latest \
		valkey-server \
		/usr/local/etc/valkey/valkey.conf

app:
	if [ -d "$(VENV)/bin" ]; then
		source $(VENV)/bin/activate;
	else
		source $(VENV)/Scripts/activate;
	fi
	export OAUTHLIB_INSECURE_TRANSPORT=1;
	$(VENV)/bin/python -m capellacollab.__main__

scheduler:
	$(VENV)/bin/python \
		-m capellacollab.cli scheduler run

coverage:
	pytest \
		--cov-report term \
		--cov-report html \
		tests/

generate-archival:
	python generate_git_archival.py

install: generate-archival
	if [ ! -d "$(VENV)" ]; \
		then printf "\033[0;31mThe directory $$(readlink -f $(VENV)) doesn't exist. A venv will be created now.\n\033[0m" && \
		uv venv $(VENV) --python 3.12;
	fi
	uv pip install -e ".[dev]" --python $(VENV)/bin/python

openapi:
	$(VENV)/bin/python \
		-m capellacollab.cli openapi generate \
		--remove-default-keys \
		--remove-min-max-keys \
		--skip-error-responses \
		--remove-unique-items-keys \
		--remove-security-schemes \
		/tmp/openapi.json

openapi-ui:
	$(VENV)/bin/python \
		-m capellacollab.cli openapi generate \
		/tmp/openapi-ui.json

import-rsa-key:
	$(VENV)/bin/python \
		-m capellacollab.cli keys import \
		/tmp/private.key

dev: database valkey app

cleanup:
	docker stop capella-collab-postgres
	docker rm capella-collab-postgres

dump:
	docker run -e PGPASSWORD=$(DB_PASSWORD) --entrypoint pg_dump --network host postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME) > $$(pwd)/../local/tmp.sql

psql:
	docker run -e PGPASSWORD=$(DB_PASSWORD) -it --network host --entrypoint="psql" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME)

clear:
	echo "DROP DATABASE $(DB_NAME); CREATE DATABASE $(DB_NAME);" | docker run -e PGPASSWORD=$(DB_PASSWORD) -i --network host --entrypoint="psql" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' postgres
	$(MAKE) trigger-reload

trigger-reload:
	touch trigger_reload.yml && rm trigger_reload.yml

load: clear
	cat $(DATABASE_LOAD_FILE) | docker run -i -e PGPASSWORD=$(DB_PASSWORD) --network host --entrypoint="psql" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME)

save:
	docker run -i -e PGPASSWORD=$(DB_PASSWORD) --network host --entrypoint="pg_dump" postgres:latest -h 'localhost' -p $(DB_PORT) -U '$(DB_USER)' $(DB_NAME) > $(DATABASE_SAVE_DIR)/$(shell date +"%FT%T").sql
