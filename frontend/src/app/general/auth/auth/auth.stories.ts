/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockMetadata,
  mockMetadataServiceProvider,
} from 'src/storybook/metadata';
import { mockActivatedRouteProvider } from 'src/storybook/routes';
import { AuthComponent } from './auth.component';

const meta: Meta<AuthComponent> = {
  title: 'General Components/Authentication',
  component: AuthComponent,
  decorators: [
    moduleMetadata({
      providers: [mockMetadataServiceProvider(mockMetadata)],
    }),
  ],
};

export default meta;
type Story = StoryObj<AuthComponent>;

export const IdentityProviderError: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockActivatedRouteProvider({
          error: 'access_denied',
          error_description: 'This is the error description.',
          error_uri: 'https://example.com/error',
        }),
      ],
    }),
  ],
};

export const Logout: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockActivatedRouteProvider({
          reason: 'logout',
        }),
      ],
    }),
  ],
};

export const Login: Story = {};

export const SessionExpired: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockActivatedRouteProvider({
          reason: 'session-expired',
        }),
      ],
    }),
  ],
};
