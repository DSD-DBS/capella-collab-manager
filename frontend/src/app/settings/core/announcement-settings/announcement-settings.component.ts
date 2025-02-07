/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatFormFieldModule } from '@angular/material/form-field';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { AnnouncementWrapperService } from 'src/app/general/announcement/announcement.service';
import { EditAnnouncementComponent } from './edit-announcement/edit-announcement/edit-announcement.component';

@Component({
  selector: 'app-announcement-settings',
  templateUrl: './announcement-settings.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatExpansionModule,
    NgxSkeletonLoaderModule,
    EditAnnouncementComponent,
  ],
})
export class AnnouncementSettingsComponent {
  public announcementWrapperService = inject(AnnouncementWrapperService);
}
