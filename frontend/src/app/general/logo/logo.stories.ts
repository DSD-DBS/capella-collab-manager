/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { mockNavbarServiceProvider } from '../../../storybook/navbar';
import { LogoComponent } from './logo.component';

const meta: Meta<LogoComponent> = {
  title: 'General Components/Logo',
  component: LogoComponent,
};

export default meta;
type Story = StoryObj<LogoComponent>;

export const BaseLogo: Story = {
  args: {},
};

export const BaseWithStaging: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockNavbarServiceProvider(
          [],
          undefined,
          {
            show: true,
            variant: 'warning',
            text: 'Staging',
          },
          true,
        ),
      ],
    }),
  ],
};

export const NarrowLogo: Story = {
  args: {},
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

export const WideLogo: Story = {
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
