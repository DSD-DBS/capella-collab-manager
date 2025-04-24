/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  componentWrapperDecorator,
  Meta,
  moduleMetadata,
  StoryObj,
} from '@storybook/angular';
import { mockAuthenticationWrapperServiceProvider } from 'src/storybook/auth';
import {
  mockBadge,
  mockNavbarItems,
  mockNavbarServiceProvider,
} from 'src/storybook/navbar';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
} from 'src/storybook/user';
import { MOBILE_VIEWPORT } from '../../../../.storybook/preview';
import { NavBarMenuComponent } from './nav-bar-menu.component';

const meta: Meta<NavBarMenuComponent> = {
  title: 'General Components/Side Navbar',
  component: NavBarMenuComponent,
  decorators: [
    moduleMetadata({
      providers: [
        mockNavbarServiceProvider(mockNavbarItems, undefined, mockBadge, true),
        mockAuthenticationWrapperServiceProvider(),
      ],
    }),
    componentWrapperDecorator(
      (story) =>
        `<div class="rounded-r-material border w-fit h-screen overflow-y-auto shadow-lg">
            ${story}
        </div>`,
    ),
  ],
  parameters: {
    layout: 'fullscreen',
    viewport: {
      defaultViewport: 'mobile1',
    },
    screenshot: {
      viewport: MOBILE_VIEWPORT,
      viewports: [],
    },
  },
};

export default meta;
type Story = StoryObj<NavBarMenuComponent>;

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
