/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { mockUser, MockUserService } from 'src/storybook/user';
import { HeaderComponent } from './header.component';

const meta: Meta<HeaderComponent> = {
  title: 'General Components / Header',
  component: HeaderComponent,
};

export default meta;
type Story = StoryObj<HeaderComponent>;

export const NormalUser: Story = {
  args: {},
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
  parameters: {
    chromatic: { viewports: [400, 1920] },
  },
};

export const Administrator: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserWrapperService,
          useFactory: () =>
            new MockUserService({ ...mockUser, role: 'administrator' }),
        },
      ],
    }),
  ],
  parameters: {
    chromatic: { viewports: [1920] },
  },
};
