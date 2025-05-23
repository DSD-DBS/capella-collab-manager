/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockBadge,
  mockNavbarItems,
  mockNavbarServiceProvider,
} from 'src/storybook/navbar';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { HeaderComponent } from './header.component';

const meta: Meta<HeaderComponent> = {
  title: 'General Components/Header',
  component: HeaderComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockNavbarServiceProvider(mockNavbarItems, undefined, mockBadge, true),
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<HeaderComponent>;

export const NormalUser: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockOwnUserWrapperServiceProvider(mockUser)],
    }),
  ],
};

export const Administrator: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockOwnUserWrapperServiceProvider({
          ...mockUser,
          role: 'administrator',
        }),
      ],
    }),
  ],
};
