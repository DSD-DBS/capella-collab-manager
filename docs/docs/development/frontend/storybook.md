<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Storybook

Storybook is a tool for developing UI components in isolation. Stories are
automatically build and pushed to Chromatic in the pipeline and visual changes
in stories are detected automatically.

In addition, Storybook can be used for easy testing of components locally.

## Run storybook locally

To run Storybook locally, execute the following command:

```bash
make -C frontend storybook
```

## Mock Angular services

You can mock services with the `moduleMetadata` decorator in Storybook. Here is
one example how to mock the projectUser to display the component for different
access levels:

```js
class MockProjectUserService implements Partial<ProjectUserService> {
  role: ProjectUserRole

  constructor(role: ProjectUserRole) {
    this.role = role
  }

  verifyRole(requiredRole: ProjectUserRole): boolean {
    const roles = ['user', 'manager', 'administrator']
    return roles.indexOf(requiredRole) <= roles.indexOf(this.role)
  }
}

export const ExampleStory: Story = {
  args: {
    ...
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('user'),
        },
      ],
    }),
  ],
}
```
