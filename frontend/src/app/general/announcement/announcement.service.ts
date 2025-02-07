/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { computed, inject, Injectable, signal } from '@angular/core';
import { AnnouncementResponse, AnnouncementsService } from 'src/app/openapi';
import { z } from 'zod';

const dismissedAnnouncementsSchema = z.array(
  z.object({
    id: z.number(),
    date: z.coerce.date(),
  }),
);

export type DismissedAnnouncements = z.infer<
  typeof dismissedAnnouncementsSchema
>;

@Injectable({
  providedIn: 'root',
})
export class AnnouncementWrapperService {
  LOCAL_STORAGE_DISMISSED_ANNOUNCEMENT_KEY =
    'capellaCollabDismissedAnnouncements';

  public announcements = signal<AnnouncementResponse[] | undefined>(undefined);
  public dismissedAnnouncements = signal<DismissedAnnouncements>([]);
  private announcementsService = inject(AnnouncementsService);
  public visibleAnnouncements = computed(() => {
    const announcements = this.announcements();
    if (!announcements) return [];

    return announcements.filter(
      (announcement) =>
        !this.dismissedAnnouncements().find((dismissedAnnouncement) => {
          return (
            dismissedAnnouncement.id === announcement.id &&
            announcement.dismissible
          );
        }),
    );
  });

  constructor() {
    this.refreshAnnouncements();
  }

  dismissAnnouncement(announcementId: number): void {
    this.dismissedAnnouncements.set([
      ...this.dismissedAnnouncements(),
      { id: announcementId, date: new Date() },
    ]);
    localStorage.setItem(
      this.LOCAL_STORAGE_DISMISSED_ANNOUNCEMENT_KEY,
      JSON.stringify(this.dismissedAnnouncements()),
    );
  }

  resetDismissedAnnouncements(): void {
    this.dismissedAnnouncements.set([]);
    localStorage.removeItem(this.LOCAL_STORAGE_DISMISSED_ANNOUNCEMENT_KEY);
  }

  refreshAnnouncements(): void {
    const localDismissedAnnouncements = localStorage.getItem(
      this.LOCAL_STORAGE_DISMISSED_ANNOUNCEMENT_KEY,
    );
    try {
      const result = dismissedAnnouncementsSchema.safeParse(
        JSON.parse(localDismissedAnnouncements ?? '[]'),
      );
      if (result.success) {
        this.dismissedAnnouncements.set(result.data);
      }
    } catch (e) {
      console.error(e);
      localStorage.removeItem(this.LOCAL_STORAGE_DISMISSED_ANNOUNCEMENT_KEY);
    }
    this.announcementsService.getAnnouncements().subscribe((res) => {
      this.announcements.set(res.sort((a, b) => a.id - b.id));
    });
  }
}
