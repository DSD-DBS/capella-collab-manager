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
import { mockNavbarServiceProvider } from '../../../../storybook/navbar';
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
        mockNavbarServiceProvider(
          [],
          '/test-assets/wide_logo.svg',
          {
            show: true,
            variant: 'success',
            text: 'Production',
          },
          true,
        ),
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
        mockNavbarServiceProvider(
          [],
          '/test-assets/wide_logo.svg',
          {
            show: true,
            variant: 'success',
            text: 'Production',
          },
          true,
        ),
      ],
    }),
  ],
};

export const Login: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockNavbarServiceProvider(
          [],
          '/test-assets/wide_logo.svg',
          {
            show: true,
            variant: 'success',
            text: 'Production',
          },
          true,
        ),
      ],
    }),
  ],
};

export const NarrowLogo: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockNavbarServiceProvider(
          [],
          '/test-assets/narrow_logo.svg',
          {
            show: true,
            variant: 'success',
            text: 'Production',
          },
          true,
        ),
      ],
    }),
  ],
};

export const NoBadge: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockNavbarServiceProvider(
          [],
          '/test-assets/wide_logo.svg',
          {
            show: false,
            variant: 'success',
            text: 'Production',
          },
          true,
        ),
      ],
    }),
  ],
};

export const LogoLoading: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockNavbarServiceProvider(
          [],
          '/test-assets/wide_logo.svg',
          {
            show: true,
            variant: 'success',
            text: 'Production',
          },
          false,
        ),
      ],
    }),
  ],
};

export const SessionExpired: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockActivatedRouteProvider({
          reason: 'session-expired',
        }),
        mockNavbarServiceProvider(
          [],
          '/test-assets/wide_logo.svg',
          {
            show: true,
            variant: 'success',
            text: 'Production',
          },
          true,
        ),
      ],
    }),
  ],
};

export const UserBlocked: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        mockActivatedRouteProvider({
          reason: 'blocked',
        }),
        mockNavbarServiceProvider(
          [],
          '/test-assets/wide_logo.svg',
          {
            show: true,
            variant: 'success',
            text: 'Production',
          },
          true,
        ),
      ],
    }),
  ],
};
