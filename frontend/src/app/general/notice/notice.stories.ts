/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { NoticeLevel } from 'src/app/openapi';
import {
  mockNotice,
  mockNoticeWrapperServiceProvider,
} from 'src/storybook/notices';
import { NoticeComponent } from './notice.component';

const meta: Meta<NoticeComponent> = {
  title: 'General Components/Notices',
  component: NoticeComponent,
};

export default meta;
type Story = StoryObj<NoticeComponent>;

export const AllLevels: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockNoticeWrapperServiceProvider(
          Object.values(NoticeLevel).map((level) => ({
            ...mockNotice,
            title: 'This is an example notice with level ' + level,
            level,
          })),
        ),
      ],
    }),
  ],
};
