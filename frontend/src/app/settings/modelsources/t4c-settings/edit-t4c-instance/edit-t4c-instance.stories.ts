/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ActivatedRoute } from '@angular/router';
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { userEvent, within } from '@storybook/test';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import { T4CLicenseServerWrapperService } from 'src/app/services/settings/t4c-license-server.service';
import { MockActivedRoute } from 'src/storybook/routes';
import {
  MockT4CInstanceWrapperService,
  MockT4CLicenseServerWrapperService,
  mockT4CInstance,
  mockT4CLicenseServer,
} from 'src/storybook/t4c';
import { mockToolVersion } from 'src/storybook/tool';
import { EditT4CInstanceComponent } from './edit-t4c-instance.component';

const meta: Meta<EditT4CInstanceComponent> = {
  title: 'Settings Components/Modelsources/T4C/Server Instance',
  component: EditT4CInstanceComponent,
  args: {
    capellaVersions: [mockToolVersion],
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CLicenseServerWrapperService,
          useFactory: () =>
            new MockT4CLicenseServerWrapperService(mockT4CLicenseServer, [
              mockT4CLicenseServer,
            ]),
        },
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<EditT4CInstanceComponent>;

export const AddInstance: Story = {
  args: {},
};

export const ExistingInstance: Story = {
  args: {
    existing: true,
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
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              instance: -1,
            }),
        },
      ],
    }),
  ],
};

export const EditExistingInstance: Story = {
  args: {},
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
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              instance: -1,
            }),
        },
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const editButton = canvas.getByTestId('edit-button');
    await userEvent.click(editButton);
  },
};

export const ArchivedInstance: Story = {
  args: {
    isArchived: true,
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
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              instance: -1,
            }),
        },
      ],
    }),
  ],
};
