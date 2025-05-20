<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Security Scanning

## Code Scanning

The frontend and backend code is scanned for vulnerabilities using
[CodeQL](https://codeql.github.com/). The scanning results are available in the
GitHub Security tab.

All containers are scanned in the pipeline automatically.

## Secret Scanning

Secrets are scanned automatically by
[GitHub](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning).

## Container Scanning

The built Docker images are scanned for high and critical vulnerabilities using
[Trivy](https://github.com/aquasecurity/trivy-action).
