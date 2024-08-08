/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { of } from 'rxjs';
import { UserWrapperService } from 'src/app/services/user/user.service';
import { mockUser, MockUserService } from 'src/storybook/user';
import { NavBarItem, NavBarService } from '../nav-bar/nav-bar.service';
import { HeaderComponent } from './header.component';

const meta: Meta<HeaderComponent> = {
  title: 'General Components / Header',
  component: HeaderComponent,
};

export default meta;
type Story = StoryObj<HeaderComponent>;

class MockNavbarService implements Partial<NavBarService> {
  readonly navbarItems$ = of<NavBarItem[]>([
    {
      name: 'Projects',
      requiredRole: 'user',
    },
    {
      name: 'Sessions',
      requiredRole: 'user',
    },
    {
      name: 'Session viewer',
      requiredRole: 'user',
    },
    {
      name: 'Session overview',
      requiredRole: 'administrator',
    },
    {
      name: 'Prometheus',
      requiredRole: 'administrator',
      icon: 'open_in_new',
      href: '#',
    },
    {
      name: 'Grafana',
      requiredRole: 'administrator',
      icon: 'open_in_new',
      href: '#',
    },
    {
      name: 'Documentation',
      requiredRole: 'user',
      icon: 'open_in_new',
      href: '#',
    },
  ]);
}

export const NormalUser: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: UserWrapperService,
          useFactory: () => new MockUserService(mockUser),
        },
        {
          provide: NavBarService,
          useFactory: () => new MockNavbarService(),
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
        {
          provide: NavBarService,
          useFactory: () => new MockNavbarService(),
        },
      ],
    }),
  ],
  parameters: {
    chromatic: { viewports: [1920] },
  },
};
