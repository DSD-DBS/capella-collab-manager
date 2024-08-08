<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Configure for your Organization

When running the Collaboration Manager in production, you may want to provide
information about the team responsible for it, as well as an imprint and
privacy policy.

You can set this information from the configuration page in the admin
interface. Navigate to _Settings_, then _Configuration_, then edit the file to
your liking.

Here, you can also edit the links in the navigation bar if you are not using
the default monitoring services.

```yaml
metadata:
    privacy_policy_url: https://example.com/privacy
    imprint_url: https://example.com/imprint
    provider: Systems Engineering Toolchain team
    authentication_provider: OAuth2
    environment: '-'
navbar:
    external_links:
        - name: Grafana
          service: grafana
          role: administrator
        - name: Prometheus
          service: prometheus
          role: administrator
        - name: Documentation
          service: documentation
          role: user
```

In addition to the default service links, you can add your own by using `href`
instead of `service`.

```yaml
navbar:
    external_links:
        - name: Example
          href: https://example.com
          role: user
```

The `role` field and can be one of `user` or `administrator`. While this will
hide the link from users without the appropriate role, it is not a security
feature, and you should make sure that the linked service enforces the
necessary access controls.
