/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  animate,
  state,
  style,
  transition,
  trigger,
} from '@angular/animations';
import { NgClass } from '@angular/common';
import { Component, inject } from '@angular/core';
import { AnnouncementWrapperService } from 'src/app/general/announcement/announcement.service';
import { AnnouncementComponent } from './announcement/announcement.component';

@Component({
  selector: 'app-announcement-list',
  templateUrl: './announcement-list.component.html',
  imports: [AnnouncementComponent, NgClass],
  animations: [
    trigger('announcementAnimation', [
      state('void', style({ height: '0' })),
      state('*', style({ height: '*' })),
      transition('* => void', animate('150ms ease-in-out')),
    ]),
  ],
})
export class AnnouncementListComponent {
  announcementWrapperService = inject(AnnouncementWrapperService);
}
