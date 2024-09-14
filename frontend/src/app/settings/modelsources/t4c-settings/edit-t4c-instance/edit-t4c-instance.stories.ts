/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import {
  MockT4CInstanceWrapperService,
  mockT4CInstance,
} from 'src/storybook/t4c';
import { mockToolVersion } from 'src/storybook/tool';
import { EditT4CInstanceComponent } from './edit-t4c-instance.component';

const meta: Meta<EditT4CInstanceComponent> = {
  title: 'Settings Components/Modelsources/T4C/Server Instance',
  component: EditT4CInstanceComponent,
};

export default meta;
type Story = StoryObj<EditT4CInstanceComponent>;

export const AddInstance: Story = {
  args: {},
};

export const ExistingInstance: Story = {
  args: {
    existing: true,
    capellaVersions: [mockToolVersion],
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CInstanceWrapperService,
          useFactory: () =>
            new MockT4CInstanceWrapperService(mockT4CInstance, [
              mockT4CInstance,
            ]),
        },
      ],
    }),
  ],
};

export const EditExistingInstance: Story = {
  args: {
    existing: true,
    editing: true,
    capellaVersions: [mockToolVersion],
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CInstanceWrapperService,
          useFactory: () =>
            new MockT4CInstanceWrapperService(mockT4CInstance, [
              mockT4CInstance,
            ]),
        },
      ],
    }),
  ],
};

export const ArchivedInstance: Story = {
  args: {
    existing: true,
    isArchived: true,
    capellaVersions: [mockToolVersion],
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CInstanceWrapperService,
          useFactory: () =>
            new MockT4CInstanceWrapperService(mockT4CInstance, [
              mockT4CInstance,
            ]),
        },
      ],
    }),
  ],
};
