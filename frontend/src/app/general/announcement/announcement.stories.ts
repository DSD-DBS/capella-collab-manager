/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { AnnouncementLevel } from 'src/app/openapi';
import {
  mockAnnouncement,
  mockAnnouncementWrapperServiceProvider,
} from 'src/storybook/announcements';
import { userEvent, within } from 'storybook/test';
import { AnnouncementListComponent } from './announcement-list.component';

const meta: Meta<AnnouncementListComponent> = {
  title: 'General Components/Announcements',
  component: AnnouncementListComponent,
  parameters: {
    screenshot: {
      delay: 1000,
    },
  },
};

export default meta;
type Story = StoryObj<AnnouncementListComponent>;

export const AllLevels: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockAnnouncementWrapperServiceProvider(
          Object.values(AnnouncementLevel).map((level, i) => ({
            ...mockAnnouncement,
            title: 'This is an example announcement with level ' + level,
            level,
            id: i,
          })),
          [],
        ),
      ],
    }),
  ],
};

export const DismissedAnnouncements: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockAnnouncementWrapperServiceProvider(
          [
            mockAnnouncement,
            {
              ...mockAnnouncement,
              message: 'This announcement is not visible',
              id: 2,
            },
            {
              ...mockAnnouncement,
              message:
                "This announcement is visible despite being dismissed, because it's not dismissible",
              dismissible: false,
              id: 3,
            },
          ],
          [{ id: 3, date: new Date() }],
        ),
      ],
    }),
  ],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const dismissButton = canvas.getByTestId('announcement-2');
    await userEvent.click(dismissButton);
  },
};
