/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { mockModel, MockModelWrapperService } from 'src/storybook/model';
import { MockProjectUserService } from 'src/storybook/project-users';
import { mockUser, MockOwnUserWrapperService } from 'src/storybook/user';
import { ModelOverviewComponent } from './model-overview.component';

const meta: Meta<ModelOverviewComponent> = {
  title: 'Model Components/Model Overview',
  component: ModelOverviewComponent,
};

export default meta;
type Story = StoryObj<ModelOverviewComponent>;

export const Loading: Story = {
  args: {},
};

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ModelWrapperService,
          useFactory: () =>
            new MockModelWrapperService(mockModel, [
              { ...mockModel, name: 'mockModel1' },
              {
                ...mockModel,
                name: 'mockModel2',
                description:
                  'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
              },
              {
                ...mockModel,
                name: 'ModelWithMissingInfo',
                version: null,
                nature: null,
              },
              {
                ...mockModel,
                name: 'Capella model',
                tool: { ...mockModel.tool, name: 'Capella' },
              },
            ]),
        },
      ],
    }),
  ],
};

export const AsProjectAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ModelWrapperService,
          useFactory: () =>
            new MockModelWrapperService(mockModel, [
              { ...mockModel, name: 'mockModel1' },
            ]),
        },
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('manager', 'write'),
        },
      ],
    }),
  ],
};

export const AsGlobalAdmin: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ModelWrapperService,
          useFactory: () =>
            new MockModelWrapperService(mockModel, [
              { ...mockModel, name: 'mockModel1' },
            ]),
        },
        {
          provide: ProjectUserService,
          useFactory: () => new MockProjectUserService('manager', 'write'),
        },
        {
          provide: OwnUserWrapperService,
          useFactory: () =>
            new MockOwnUserWrapperService({
              ...mockUser,
              role: 'administrator',
            }),
        },
      ],
    }),
  ],
};
