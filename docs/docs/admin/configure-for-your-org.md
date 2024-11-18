<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Configure for your Organization

When running the Collaboration Manager in production, you may want to provide
information about the team responsible for it.

You can set this information from the configuration page in the admin
interface. Navigate to _Settings_, then _Configuration_, then edit the file to
your liking.

## About your Organization

You can set URLs to your organization's privacy policy and imprint. These are
shown in the footer. The provider field should be used for the name of the team
responsible for the Collaboration Manager.

```yaml
metadata:
    privacy_policy_url: https://example.com/privacy
    imprint_url: https://example.com/imprint
    provider: Systems Engineering Toolchain team
    authentication_provider: OAuth2
    environment: '-'
```

## Navigation Bar

You can edit the links in the navigation bar. This can be useful if you want to
link to external resources or if you are not using the default monitoring
setup.

```yaml
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

## Feedback

!!! info "Configure SMTP server for feedback"

    For feedback to be sent, you need to configure an SMTP server in the
    `values.yaml` of the Helm chart. Have a look at the `alerting.email`
    configuration.

Capella Collaboration Manager can prompt users for feedback. This can be useful
for learning about any potential issues users may be facing.

There are several different types of feedback prompt:

-   After a session: Prompt the user for feedback after they have manually
    terminated a session.
-   On the session card: Show a feedback button on the session card.
-   In the footer: Show a feedback button in the footer.
-   Interval: Prompt the user for feedback after a certain number of hours have
    passed since the last prompt.

```yaml
feedback:
    enabled: true
    after_session: true
    on_footer: true
    on_session_card: true
    interval:
        enabled: true
        hours_between_prompt: 168
    recipients: # (1)!
        - test1@example.com
        - test2@example.com
    hint_text: Try to be specific. What happened? What were you doing?
```

Prompts that are associated with a session automatically include anonymized
metadata about the session.

1. Feedback will be sent by email to all addresses specified here.

## Beta-Testing

To test new images, you can enable the beta-testing feature. This will allow
you specify a different image tag to use. Users can self-enroll as a
beta-tester if you enable self-enrollment. Admins can always enroll themselves
and others.

```yaml
beta:
    enabled: true
    allow_self_enrollment: true
```
