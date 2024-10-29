/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { BadgeOutput } from '../../openapi';
import { NavBarService } from '../nav-bar/nav-bar.service';
import { LogoComponent } from './logo.component';

const meta: Meta<LogoComponent> = {
  title: 'General Components/Logo',
  component: LogoComponent,
};

export default meta;
type Story = StoryObj<LogoComponent>;

class MockNavbarService implements Partial<NavBarService> {
  readonly logoUrl$ = new BehaviorSubject<string | undefined>(undefined);
  readonly badge$ = new BehaviorSubject<BadgeOutput | undefined>(undefined);

  constructor(logoUrl: string | undefined, badge: BadgeOutput | undefined) {
    this.logoUrl$.next(logoUrl);
    this.badge$.next(badge);
  }
}

export const BaseLogo: Story = {
  args: {},
};

export const BaseWithStaging: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: NavBarService,
          useFactory: () =>
            new MockNavbarService(undefined, {
              show: true,
              variant: 'warning',
              text: 'Staging',
            }),
        },
      ],
    }),
  ],
};

export const NarrowLogo: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: NavBarService,
          useFactory: () =>
            new MockNavbarService('/test-assets/narrow_logo.svg', {
              show: true,
              variant: 'success',
              text: 'Production',
            }),
        },
      ],
    }),
  ],
};

export const WideLogo: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: NavBarService,
          useFactory: () =>
            new MockNavbarService('/test-assets/wide_logo.svg', {
              show: true,
              variant: 'success',
              text: 'Production',
            }),
        },
      ],
    }),
  ],
};
