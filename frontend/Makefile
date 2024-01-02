# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

export NG_FORCE_TTY=false

dev:
	ng serve --open

test:
	if [ $(shell which chromium) ]; \
	then \
		export CHROME_BIN=$(shell which chromium); \
		ng test; \
	else \
		echo "No binary for Chrome browser on your platform. Please, set "CHROME_BIN" env variable."; \
	fi
