/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ActivatedRoute } from '@angular/router';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { mockMetadata, MockMetadataService } from 'src/storybook/metadata';
import { MockActivedRoute } from 'src/storybook/routes';
import { AuthComponent } from './auth.component';

const meta: Meta<AuthComponent> = {
  title: 'General Components/Authentication',
  component: AuthComponent,
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: MetadataService,
          useFactory: () =>
            new MockMetadataService(
              mockMetadata,
              undefined,
              undefined,
              undefined,
            ),
        },
      ],
    }),
  ],
};

export default meta;
type Story = StoryObj<AuthComponent>;

export const IdentityProviderError: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              error: 'access_denied',
              error_description: 'This is the error description.',
              error_uri: 'https://example.com/error',
            }),
        },
      ],
    }),
  ],
};

export const Logout: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              reason: 'logout',
            }),
        },
      ],
    }),
  ],
};

export const Login: Story = {};

export const SessionExpired: Story = {
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: ActivatedRoute,
          useFactory: () =>
            new MockActivedRoute({
              reason: 'session-expired',
            }),
        },
      ],
    }),
  ],
};
