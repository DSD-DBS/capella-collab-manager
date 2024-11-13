/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { Observable, of } from 'rxjs';
import { UsersService, Workspace } from 'src/app/openapi';
import {
  mockUser,
  mockOwnUserWrapperServiceProvider,
  mockUserWrapperServiceProvider,
} from 'src/storybook/user';
import { UserWorkspacesComponent } from './user-workspaces.component';

class MockUserService {
  _workspaces: Workspace[] = [];

  public getWorkspacesForUser(_userId: number): Observable<Workspace[]> {
    return of(this._workspaces);
  }

  constructor(workspaces: Workspace[]) {
    this._workspaces = workspaces;
  }
}

const meta: Meta<UserWorkspacesComponent> = {
  title: 'Settings Components/Users Profile/User Workspaces',
  component: UserWorkspacesComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockOwnUserWrapperServiceProvider({
          ...mockUser,
          role: 'administrator',
        }),
        mockUserWrapperServiceProvider({ ...mockUser, id: 0 }),
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<UserWorkspacesComponent>;

export const Loading: Story = {
  args: {},
};

export const NoWorkspaces: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UsersService,
          useFactory: () => new MockUserService([]),
        },
      ],
    }),
  ],
};

export const WorkspaceOverview: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UsersService,
          useFactory: () =>
            new MockUserService([
              {
                id: 1,
                pvc_name:
                  'persistent-volume-429d805a-6904-4217-b035-8e3def3506ce',
                size: '20Gi',
              },
            ]),
        },
      ],
    }),
  ],
};
