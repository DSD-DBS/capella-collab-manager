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

## Prepare a Component

Before you can write a story for a component, you need to prepare the
component. Storybook can only recognize all imports when the component is
defined as standalone and all required modules are specified explicitly.

```ts
@Component({
  standalone: true,
  imports: [
    ... // (1)
  ],
  ...
})
```

1.  All imports that are required for the component have to be defined here
    (previously, they had to be defined in the `app.module.ts`)

    !!! warning

         Make sure to import the `RouterLink` if you use the `routerLink` attribute in the HTML template.
         Otherwise, links will break without warning.

## Add a Story and Documentation

In the same directory of the component, add a file
`{component_name}.stories.ts` and use the following code as a template:

```ts
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { Component } from './component-name.component';

const meta: Meta<YourComponent> = {
    title: 'Your Component',
    component: YourComponent,
};

export default meta;
type Story = StoryObj<YourComponent>;

export const ExampleStory: Story = {
    args: {},
};
```

## Mock Angular services

You can mock services with the `moduleMetadata` decorator in Storybook. Here is
one example how to mock the projectUser to display the component for different
access levels:

```js
class MockProjectUserService implements Partial<ProjectUserService> {
    role: ProjectUserRole;

    constructor(role: ProjectUserRole) {
        this.role = role;
    }

    verifyRole(requiredRole: ProjectUserRole): boolean {
        const roles = ['user', 'manager', 'administrator'];
        return roles.indexOf(requiredRole) <= roles.indexOf(this.role);
    }
}

const mockProjectUserServiceProvider = (role: ProjectUserRole) => {
    return {
        provide: ProjectUserService,
        useValue: new MockProjectUserService(role),
    };
};

export const ExampleStory: Story = {
    args: {},
    decorators: [
        moduleMetadata({
            providers: [mockProjectUserServiceProvider('user')],
        }),
    ],
};
```
