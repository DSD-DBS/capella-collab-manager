/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, StoryObj } from '@storybook/angular';
import MockDate from 'mockdate';
import { userToken } from '../personal-access-tokens.stories';
import { AllPersonalAccessTokensComponent } from './all-personal-access-tokens.component';

const meta: Meta<AllPersonalAccessTokensComponent> = {
  title: 'Settings Components/Personal Access Tokens Overview',
  component: AllPersonalAccessTokensComponent,
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
};

export default meta;
type Story = StoryObj<AllPersonalAccessTokensComponent>;

export const Loading: Story = {
  args: {
    tokens: undefined,
  },
};

export const NoTokens: Story = {
  args: {
    tokens: [],
  },
};

export const GlobalTokenOverview: Story = {
  args: {
    tokens: [
      userToken,
      {
        ...userToken,
        id: 2,
        title: 'This name is slightly longer',
        user: { ...userToken.user, id: 2, name: 'Visual Testing User' },
      },
      {
        ...userToken,
        id: 2,
        title: 'Another token with a long name',
        user: { ...userToken.user, id: 2, name: 'jane.doe@example.com' },
      },
    ],
  },
};
