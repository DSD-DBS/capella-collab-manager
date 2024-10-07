/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockT4CLicenseServer,
  mockT4CLicenseServerUnreachable,
  mockT4CLicenseServerUnused,
  MockT4CLicenseServerWrapperService,
} from '../../../../../storybook/t4c';
import { T4CLicenseServerWrapperService } from '../../../../services/settings/t4c-license-server.service';
import { EditT4cLicenseServerComponent } from './edit-t4c-license-server.component';

const meta: Meta<EditT4cLicenseServerComponent> = {
  title: 'Settings Components/Modelsources/T4C/License Server',
  component: EditT4cLicenseServerComponent,
};

export default meta;
type Story = StoryObj<EditT4cLicenseServerComponent>;

export const AddLicenseServer: Story = {
  args: {},
};

export const ExistingLicenseServer: Story = {
  args: {
    existing: true,
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

export const ExistingUnreachableLicenseServer: Story = {
  args: {
    existing: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CLicenseServerWrapperService,
          useFactory: () =>
            new MockT4CLicenseServerWrapperService(
              mockT4CLicenseServerUnreachable,
              [mockT4CLicenseServerUnreachable],
            ),
        },
      ],
    }),
  ],
};

export const ExistingUnusedLicenseServer: Story = {
  args: {
    existing: true,
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CLicenseServerWrapperService,
          useFactory: () =>
            new MockT4CLicenseServerWrapperService(mockT4CLicenseServerUnused, [
              mockT4CLicenseServerUnused,
            ]),
        },
      ],
    }),
  ],
};
