/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import { AuthRedirectComponent } from './auth-redirect.component';

const meta: Meta<AuthRedirectComponent> = {
  title: 'General Component/Auth Redirect',
  component: AuthRedirectComponent,
};

export default meta;
type Story = StoryObj<AuthRedirectComponent>;

export const General: Story = {
  args: {},
};
