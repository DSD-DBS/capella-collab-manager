# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export NG_FORCE_TTY=false

.ONESHELL:

dev:
	ng serve --host 0.0.0.0 --open

test:
	if [ $(shell which chromium) ]; \
	then \
		export CHROME_BIN=$(shell which chromium); \
		ng test; \
	else \
		echo "No binary for Chrome browser on your platform. Please, set "CHROME_BIN" env variable."; \
	fi

storybook:
	ng run capellacollab:storybook --quiet

openapi:
	python postprocess_openapi_schema.py
	OPENAPI_DIR=$$(mktemp -d)
	docker run --rm \
  		-v /tmp/openapi.json:/tmp/openapi.json \
		-v $$(pwd)/openapi_templates:/tmp/openapi_templates \
		-v $$OPENAPI_DIR:/tmp/output \
		-u $$(id -u $${USER}):$$(id -g $${USER}) \
		openapitools/openapi-generator-cli:v7.8.0 generate \
			-i /tmp/openapi.json \
			-t /tmp/openapi_templates \
			--global-property models,apis,supportingFiles="index.ts:api.ts:models.ts:variables.ts:configuration.ts:api.module.ts:param.ts:encoder.ts" \
			--additional-properties=fileNaming=kebab-case,legacyDiscriminatorBehavior=false \
			-g typescript-angular \
			-o /tmp/output
	cp ../LICENSES/.license_header_cc0.txt $$OPENAPI_DIR/.openapi-generator/FILES.license
	cp ../LICENSES/.license_header_cc0.txt $$OPENAPI_DIR/.openapi-generator/VERSION.license
	rsync -avh --delete $$OPENAPI_DIR/ $$(pwd)/src/app/openapi
	rm -rf $$OPENAPI_DIR
