/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj, moduleMetadata } from '@storybook/angular';
import { of } from 'rxjs';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { mockProject } from 'src/storybook/project';
import { MockUserService, mockUser } from 'src/storybook/user';
import { CommonProjectsComponent } from './common-projects.component';

const meta: Meta<CommonProjectsComponent> = {
  title: 'Settings Components/Users Profile/Common Projects',
  component: CommonProjectsComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserWrapperService,
          useFactory: () => new MockUserService(mockUser),
        },
      ],
    }),
  ],
  args: {
    _user: { ...mockUser, id: 0 },
  },
};

export default meta;
type Story = StoryObj<CommonProjectsComponent>;

export const Loading: Story = {
  args: {
    commonProjects$: of(undefined),
  },
};

export const NoCommonProjects: Story = {
  args: {
    commonProjects$: of([]),
  },
};

export const CommonProjects: Story = {
  args: {
    commonProjects$: of([
      mockProject,
      { ...mockProject, name: 'Another mock project', description: '' },
      { ...mockProject, name: 'And a third mock project' },
    ]),
  },
};
