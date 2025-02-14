/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { computed, signal } from '@angular/core';
import {
  AnnouncementWrapperService,
  DismissedAnnouncements,
} from 'src/app/general/announcement/announcement.service';
import { AnnouncementLevel, AnnouncementResponse } from 'src/app/openapi';

export const mockAnnouncement: AnnouncementResponse = {
  id: 1,
  title: 'Title of the announcement',
  message:
    'This is the message / content of an announcement. It can also contain simple HTML like links: ' +
    "<a href='https://example.com'>example.com</a>",
  level: AnnouncementLevel.Info,
  dismissible: true,
};

class MockAnnouncementWrapperService
  implements Partial<AnnouncementWrapperService>
{
  public announcements = signal<AnnouncementResponse[]>([]);
  public dismissedAnnouncements = signal<DismissedAnnouncements>([]);
  public visibleAnnouncements = computed(() => {
    return this.announcements().filter(
      (announcement) =>
        !this.dismissedAnnouncements().find((dismissedAnnouncement) => {
          return (
            dismissedAnnouncement.id === announcement.id &&
            announcement.dismissible
          );
        }),
    );
  });
  dismissAnnouncement(announcementId: number): void {
    this.dismissedAnnouncements.set([
      ...this.dismissedAnnouncements(),
      { id: announcementId, date: new Date() },
    ]);
  }

  resetDismissedAnnouncements(): void {
    this.dismissedAnnouncements.set([]);
  }

  constructor(
    notices: AnnouncementResponse[],
    dismissedAnnouncements: DismissedAnnouncements,
  ) {
    this.announcements.set(notices);
    this.dismissedAnnouncements.set(dismissedAnnouncements);
  }
}

export const mockAnnouncementWrapperServiceProvider = (
  announcements: AnnouncementResponse[],
  dismissedAnnouncements: DismissedAnnouncements,
) => {
  return {
    provide: AnnouncementWrapperService,
    useValue: new MockAnnouncementWrapperService(
      announcements,
      dismissedAnnouncements,
    ),
  };
};
