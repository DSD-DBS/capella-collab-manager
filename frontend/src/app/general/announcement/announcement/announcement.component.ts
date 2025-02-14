/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject, input } from '@angular/core';
import { MatIconButton } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MarkdownComponent, provideMarkdown } from 'ngx-markdown';
import { AnnouncementResponse } from '../../../openapi';
import { AnnouncementWrapperService } from '../announcement.service';

@Component({
  selector: 'app-announcement',
  imports: [MatIconButton, MatIconModule, MarkdownComponent],
  templateUrl: './announcement.component.html',
  styleUrls: ['./announcement.component.css'],
  providers: [provideMarkdown()],
})
export class AnnouncementComponent {
  announcement = input.required<AnnouncementResponse>();
  isPreview = input<boolean>(false);
  announcementWrapperService = inject(AnnouncementWrapperService);

  dismissAnnouncement() {
    if (!this.isPreview()) {
      this.announcementWrapperService.dismissAnnouncement(
        this.announcement().id,
      );
    }
  }
}
