/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { NoticeWrapperService } from 'src/app/general/notice/notice.service';
import { mockNotice, MockNoticeWrapperService } from 'src/storybook/notices';
import { AlertSettingsComponent } from './alert-settings.component';

const meta: Meta<AlertSettingsComponent> = {
  title: 'Settings Components / Alert Settings',
  component: AlertSettingsComponent,
};

export default meta;
type Story = StoryObj<AlertSettingsComponent>;

export const Loading: Story = {
  args: {},
};

export const NoAlerts: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: NoticeWrapperService,
          useFactory: () => new MockNoticeWrapperService([]),
        },
      ],
    }),
  ],
};

export const SomeAlerts: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        {
          provide: NoticeWrapperService,
          useFactory: () =>
            new MockNoticeWrapperService([
              mockNotice,
              { ...mockNotice, id: 2 },
            ]),
        },
      ],
    }),
  ],
};
