/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import MockDate from 'mockdate';
import { AllTokensService } from '../../../openapi';
import { userToken } from '../personal-access-tokens.stories';
import { AllPersonalAccessTokensComponent } from './all-personal-access-tokens.component';

class MockAllTokensService implements Partial<AllTokensService> {
  // @ts-expect-error This doesn't have to return anything
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  getAllTokens() {}
}

const meta: Meta<AllPersonalAccessTokensComponent> = {
  title: 'Settings Components/Personal Access Tokens Overview',
  component: AllPersonalAccessTokensComponent,
  beforeEach: () => {
    MockDate.set(new Date('2024-05-01'));
  },
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: AllTokensService,
          useFactory: () => new MockAllTokensService(),
        },
      ],
    }),
  ],
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

export const TokenOverview: Story = {
  args: {
    tokens: [userToken],
  },
};
