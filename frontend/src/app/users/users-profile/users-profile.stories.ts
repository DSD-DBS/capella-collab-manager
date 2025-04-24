/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { mockUser, mockUserWrapperServiceProvider } from 'src/storybook/user';
import { UsersProfileComponent } from './users-profile.component';

const meta: Meta<UsersProfileComponent> = {
  title: 'Settings Components/Users Profile/Profile Overview',
  component: UsersProfileComponent,
};

export default meta;
type Story = StoryObj<UsersProfileComponent>;

export const Basic: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockUserWrapperServiceProvider({ ...mockUser, id: 0 })],
    }),
  ],
};

export const BlockedUser: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockUserWrapperServiceProvider({ ...mockUser, id: 0, blocked: true }),
      ],
    }),
  ],
};
