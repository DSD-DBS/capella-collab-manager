/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  MockOwnUserWrapperService,
  mockUser,
  MockUserWrapperService,
} from '../../../../storybook/user';
import { OwnUserWrapperService } from '../../../services/user/user.service';
import { UserWrapperService } from '../../user-wrapper/user-wrapper.service';
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
        {
          provide: OwnUserWrapperService,
          useFactory: () => new MockOwnUserWrapperService(mockUser),
        },
        {
          provide: UserWrapperService,
          useFactory: () => new MockUserWrapperService(mockUser),
        },
      ],
    }),
  ],
};

export const OptOutOfBeta: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: OwnUserWrapperService,
          useFactory: () => new MockOwnUserWrapperService(mockUser),
        },
        {
          provide: UserWrapperService,
          useFactory: () =>
            new MockUserWrapperService({ ...mockUser, beta_tester: true }),
        },
      ],
    }),
  ],
};
