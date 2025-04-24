/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { mockSimpleToolModel } from 'src/storybook/model';
import {
  mockT4CInstance,
  mockT4CRepositoryWrapperServiceProvider,
} from 'src/storybook/t4c';
import { T4CInstanceSettingsComponent } from './t4c-instance-settings.component';

const meta: Meta<T4CInstanceSettingsComponent> = {
  title: 'Settings Components/Modelsources/T4C/Repositories',
  component: T4CInstanceSettingsComponent,
  args: {
    instance: mockT4CInstance,
  },
};

export default meta;
type Story = StoryObj<T4CInstanceSettingsComponent>;

export const Repositories: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CRepositoryWrapperServiceProvider([
          {
            id: 1,
            name: 'online-repository',
            instance: mockT4CInstance,
            status: 'ONLINE',
            integrations: [],
          },
          {
            id: 2,
            name: 'offline-repository',
            instance: mockT4CInstance,
            status: 'OFFLINE',
            integrations: [],
          },
          {
            id: 3,
            name: 'not-found-repository',
            instance: mockT4CInstance,
            status: 'NOT_FOUND',
            integrations: [],
          },
          {
            id: 4,
            name: 'loading-repository',
            instance: mockT4CInstance,
            status: 'LOADING',
            integrations: [],
          },
          {
            id: 5,
            name: 'initial-repository',
            instance: mockT4CInstance,
            status: 'INITIAL',
            integrations: [],
          },
          {
            id: 6,
            name: 'unreachable-repository',
            instance: mockT4CInstance,
            status: 'INSTANCE_UNREACHABLE',
            integrations: [],
          },
        ]),
      ],
    }),
  ],
};

export const RepositoriesWithIntegrations: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CRepositoryWrapperServiceProvider([
          {
            id: 1,
            name: 'online-repository',
            instance: mockT4CInstance,
            status: 'ONLINE',
            integrations: [
              {
                id: 1,
                name: 'mockModel',
                model: mockSimpleToolModel,
              },
              {
                id: 2,
                name: 'mockModel 2',
                model: mockSimpleToolModel,
              },
            ],
          },
          {
            id: 2,
            name: 'offline-repository',
            instance: mockT4CInstance,
            status: 'OFFLINE',
            integrations: [
              {
                id: 2,
                name: 'mockModel 3',
                model: mockSimpleToolModel,
              },
            ],
          },
          {
            id: 3,
            name: 'not-found-repository',
            instance: mockT4CInstance,
            status: 'NOT_FOUND',
            integrations: [],
          },
        ]),
      ],
    }),
  ],
};

export const AddRepositories: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockT4CRepositoryWrapperServiceProvider([
          {
            id: 1,
            name: 'test',
            instance: mockT4CInstance,
            status: 'ONLINE',
            integrations: [],
          },
        ]),
      ],
    }),
  ],
};
