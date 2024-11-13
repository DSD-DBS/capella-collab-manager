/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockOwnUserWrapperServiceProvider,
  mockUser,
  mockUserWrapperServiceProvider,
} from '../../../../storybook/user';
import { BetaTestingComponent } from './beta-testing.component';

const meta: Meta<BetaTestingComponent> = {
  title: 'Settings Components/Users Profile/Beta Testing',
  component: BetaTestingComponent,
};

export default meta;
type Story = StoryObj<BetaTestingComponent>;

export const OptIntoBeta: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockOwnUserWrapperServiceProvider(mockUser),
        mockUserWrapperServiceProvider(mockUser),
      ],
    }),
  ],
};

export const OptOutOfBeta: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockOwnUserWrapperServiceProvider(mockUser),
        mockUserWrapperServiceProvider({ ...mockUser, beta_tester: true }),
      ],
    }),
  ],
};
