/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { T4CRepositoryWrapperService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import {
  MockT4CRepositoryWrapperService,
  mockT4CInstance,
} from 'src/storybook/t4c';
import { T4CInstanceSettingsComponent } from './t4c-instance-settings.component';

const meta: Meta<T4CInstanceSettingsComponent> = {
  title: 'Settings Components / Modelsources / T4C / Repositories',
  component: T4CInstanceSettingsComponent,
  parameters: {
    chromatic: { viewports: [380] },
  },
};

export default meta;
type Story = StoryObj<T4CInstanceSettingsComponent>;

export const Repositories: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CRepositoryWrapperService,
          useFactory: () =>
            new MockT4CRepositoryWrapperService([
              {
                id: 1,
                name: 'online-repository',
                instance: mockT4CInstance,
                status: 'ONLINE',
              },
              {
                id: 2,
                name: 'offline-repository',
                instance: mockT4CInstance,
                status: 'OFFLINE',
              },
              {
                id: 3,
                name: 'not-found-repository',
                instance: mockT4CInstance,
                status: 'NOT_FOUND',
              },
              {
                id: 4,
                name: 'loading-repository',
                instance: mockT4CInstance,
                status: 'LOADING',
              },
              {
                id: 5,
                name: 'initial-repository',
                instance: mockT4CInstance,
                status: 'INITIAL',
              },
              {
                id: 6,
                name: 'unreachable-repository',
                instance: mockT4CInstance,
                status: 'INSTANCE_UNREACHABLE',
              },
            ]),
        },
      ],
    }),
  ],
};

export const AddRepositories: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: T4CRepositoryWrapperService,
          useFactory: () =>
            new MockT4CRepositoryWrapperService([
              {
                id: 1,
                name: 'test',
                instance: mockT4CInstance,
                status: 'ONLINE',
              },
            ]),
        },
      ],
    }),
  ],
};
