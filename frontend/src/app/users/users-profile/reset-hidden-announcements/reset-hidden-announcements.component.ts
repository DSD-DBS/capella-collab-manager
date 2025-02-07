/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, computed, inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { AnnouncementWrapperService } from '../../../general/announcement/announcement.service';

@Component({
  selector: 'app-reset-hidden-announcements',
  imports: [MatButton],
  templateUrl: './reset-hidden-announcements.component.html',
})
export class ResetHiddenAnnouncementsComponent {
  public announcementWrapperService = inject(AnnouncementWrapperService);

  hiddenAnnouncements = computed(() => {
    return this.announcementWrapperService
      .dismissedAnnouncements()
      .filter((announcement) => {
        return this.announcementWrapperService
          .announcements()
          ?.find((visibleAnnouncement) => {
            return visibleAnnouncement.id === announcement.id;
          });
      });
  });
}
