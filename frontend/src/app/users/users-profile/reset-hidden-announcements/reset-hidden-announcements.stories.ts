/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import {
  mockAnnouncement,
  mockAnnouncementWrapperServiceProvider,
} from '../../../../storybook/announcements';
import { ResetHiddenAnnouncementsComponent } from './reset-hidden-announcements.component';

const meta: Meta<ResetHiddenAnnouncementsComponent> = {
  title: 'Settings Components/Users Profile/Reset Hidden Announcements',
  component: ResetHiddenAnnouncementsComponent,
};

export default meta;
type Story = StoryObj<ResetHiddenAnnouncementsComponent>;

export const NoDismissedAnnouncements: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockAnnouncementWrapperServiceProvider([mockAnnouncement], []),
      ],
    }),
  ],
};

export const DismissedAnnouncementThatIsNoLongerVisible: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockAnnouncementWrapperServiceProvider(
          [mockAnnouncement],
          [{ id: -1, date: new Date() }],
        ),
      ],
    }),
  ],
};

export const OneDismissedAnnouncement: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockAnnouncementWrapperServiceProvider(
          [mockAnnouncement],
          [{ id: 1, date: new Date() }],
        ),
      ],
    }),
  ],
};

export const TwoDismissedAnnouncements: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockAnnouncementWrapperServiceProvider(
          [mockAnnouncement, { ...mockAnnouncement, id: 2 }],
          [
            { id: 1, date: new Date() },
            { id: 2, date: new Date() },
          ],
        ),
      ],
    }),
  ],
};
