# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

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
