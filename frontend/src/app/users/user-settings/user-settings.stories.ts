/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { User } from 'src/app/openapi';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
  mockUserWrapperServiceProvider,
} from 'src/storybook/user';
import { UserSettingsComponent } from './user-settings.component';

const meta: Meta<UserSettingsComponent> = {
  title: 'Settings Components/User Settings',
  component: UserSettingsComponent,
};

export default meta;
type Story = StoryObj<UserSettingsComponent>;

export const Loading: Story = {
  args: {},
};

const loggedInUser: User = {
  ...mockUser,
  name: 'currentlyLoggedInUser',
  role: 'administrator',
  id: 132,
};

export const Overview: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockUserWrapperServiceProvider(undefined, [
          {
            ...mockUser,
            role: 'administrator',
            name: 'globalAdministrator1',
          },
          {
            ...mockUser,
            role: 'administrator',
            name: 'globalAdministrator2',
          },
          loggedInUser,
          mockUser,
          {
            ...mockUser,
            name: 'userWithReallyLongNameThatHasToBeWrapped',
          },
        ]),
        mockOwnUserWrapperServiceProvider(loggedInUser),
      ],
    }),
  ],
};
