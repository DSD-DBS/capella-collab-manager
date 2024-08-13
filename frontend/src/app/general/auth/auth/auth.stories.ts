/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { convertToParamMap } from '@angular/router';
import { Meta, StoryObj } from '@storybook/angular';
import { AuthComponent } from './auth.component';

const meta: Meta<AuthComponent> = {
  title: 'General Components / Authentication',
  component: AuthComponent,
};

export default meta;
type Story = StoryObj<AuthComponent>;

export const IdentityProviderError: Story = {
  args: {
    params: convertToParamMap({
      error: 'access_denied',
      error_description: 'This is the error description.',
      error_uri: 'https://example.com/error',
    }),
  },
};

export const Logout: Story = {
  args: {
    reason: 'logout',
  },
};

export const Login: Story = {};

export const SessionExpired: Story = {
  args: {
    reason: 'session-expired',
  },
};
