<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Authentication Methods

!!! info

    If you want to authenticate against the API using a personal access token,
    please refer to the [API documentation](../../api/index.md#authentication).

The Capella Collaboration Manager is developed to work together with OpenID
Connect (OIDC) compliant identity providers. Since we don't support any other
authentication methods, it is required to have an OIDC compliant identity
provider to use the Capella Collaboration Manager.

The authentication has to be configured in the `backend.authentication` section
of the `values.yaml`.

If no running OpenID Connect server is available in your environment, you can
set up Keycloak as an intermediate identity provider.
[Keycloak](https://www.keycloak.org/) is an open-source identity and access
management solution that supports many common protocols like OAuth 2.0, SAML
2.0, LDAP, and others.

Learn more about how to integrate the Capella Collaboration Manager in Keycloak
[here](./keycloak/index.md).
