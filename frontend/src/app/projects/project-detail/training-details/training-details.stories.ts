/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockModel,
  mockModelWrapperServiceProvider,
} from 'src/storybook/model';
import { mockProjectUserServiceProvider } from 'src/storybook/project-users';
import { TrainingDetailsComponent } from './training-details.component';

const meta: Meta<TrainingDetailsComponent> = {
  title: 'Project Components/Training Details',
  component: TrainingDetailsComponent,
};

export default meta;
type Story = StoryObj<TrainingDetailsComponent>;

export const Loading: Story = {};

export const NoModel: Story = {
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(undefined, [])],
    }),
  ],
};

export const NoModelAsProjectLead: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectUserServiceProvider('manager'),
        mockModelWrapperServiceProvider(undefined, []),
      ],
    }),
  ],
};

const readme = `
# Heading level 1
## Heading level 2
### Heading level 3

This is an example of **bold text**.
And another example with *italics*.

- list
  - sublist
  - test
- item 2

1. Ordered list
2. Test

This is a example text with a [link to an external page](https://example.com).

You can also use code blocks:

${'```'}zsh
git clone --recurse-submodules https://github.com/dbinfrago/capella-collab-manager.git
cd capella-collab-manager
${'```'}
`;

export const Loaded: Story = {
  args: {
    readmes: new Map([[mockModel.slug, { readme }]]),
  },
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(undefined, [mockModel])],
    }),
  ],
};

export const ReadmeNotFound: Story = {
  args: {
    readmes: new Map([[mockModel.slug, { errorCode: 'FILE_NOT_FOUND' }]]),
  },
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(undefined, [mockModel])],
    }),
  ],
};

export const ReadmeLoadingFailed: Story = {
  args: {
    readmes: new Map([
      [
        mockModel.slug,
        {
          errorCode: 'GIT_REPOSITORY_NOT_FOUND',
          errorMessage: `No Git repository with the ID '1' found for the model with slug ${mockModel.slug}.`,
        },
      ],
    ]),
  },
  decorators: [
    moduleMetadata({
      providers: [mockModelWrapperServiceProvider(undefined, [mockModel])],
    }),
  ],
};

export const LoadedAsProjectLead: Story = {
  args: {
    readmes: new Map([[mockModel.slug, { readme }]]),
  },
  decorators: [
    moduleMetadata({
      providers: [
        mockProjectUserServiceProvider('manager'),
        mockModelWrapperServiceProvider(undefined, [mockModel]),
      ],
    }),
  ],
};
