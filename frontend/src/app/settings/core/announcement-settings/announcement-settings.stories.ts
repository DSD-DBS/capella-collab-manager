/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockAnnouncement,
  mockAnnouncementWrapperServiceProvider,
} from 'src/storybook/announcements';
import { AnnouncementSettingsComponent } from './announcement-settings.component';

const meta: Meta<AnnouncementSettingsComponent> = {
  title: 'Settings Components/Announcement Settings',
  component: AnnouncementSettingsComponent,
};

export default meta;
type Story = StoryObj<AnnouncementSettingsComponent>;

export const Loading: Story = {
  args: {},
};

export const NoAnnouncements: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [mockAnnouncementWrapperServiceProvider([], [])],
    }),
  ],
};

export const SomeAnnouncements: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockAnnouncementWrapperServiceProvider(
          [mockAnnouncement, { ...mockAnnouncement, id: 2 }],
          [],
        ),
      ],
    }),
  ],
};
