<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Activate direct RDP access to sessions

The Collaboration Manager provides a feature to enable direct RDP[^1]
connections to sessions. A direct connection is more reliable than the
web-based connection via Guacamole.

However, it comes also with some security implications. Therefore, it is
disabled by default.

[^1]: Remote Desktop Protocol

## Possible security implications

- The RDP hostname, username and password are exposed to the user. If the user
  shares this data and does not treat it confidentially, third parties can
  access the session. Withdrawal is only possible by ending the session. Each
  session receives new credentials and old ones are no longer valid.
- The session is vulnerable to possible RDP security vulnerabilities. It is
  therefore important to always use the latest version of our Docker images.

## Technical background

To expose the sessions, we request a public Kubernetes service of type
`LoadBalancer`. More information is available in the
[Kubernetes documentation](https://kubernetes.io/docs/concepts/services-networking/service/#loadbalancer).

Most cloud providers have a `loadBalancerClass` implemented. If you run your
own cluster on a virtual machine, the networking configuration is more complex.
In this case, you can stick to the web-based connection via Guacamole.

## Enable direct RDP access

To enable direct RDP access, navigate to the Menu, select `Settings` and then
`General configuration`.

You should see a YAML editor. Set the following options in the configuration:

```yaml
sessions:
  connections:
    directRDP:
      enabled: true

kubernetes:
  loadBalancer:
    annotations:
      # Example for AWS, more information below.
      service.beta.kubernetes.io/aws-load-balancer-internal: 'true'
```

To get a public route assigned, most cloud providers require a specific
annotation on the Kubernetes service to work. A list of supported cloud
providers and their annotations can be found in the Kubernetes documentation:
[Internal load balancer](https://kubernetes.io/docs/concepts/services-networking/service/#internal-load-balancer).
