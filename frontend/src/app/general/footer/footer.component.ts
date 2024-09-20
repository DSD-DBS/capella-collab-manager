/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { VersionComponent } from 'src/app/general/metadata/version/version.component';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { FeedbackWrapperService } from '../../sessions/feedback/feedback.service';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  standalone: true,
  imports: [AsyncPipe, VersionComponent, MatIconModule],
})
export class FooterComponent {
  constructor(
    public dialog: MatDialog,
    public metadataService: MetadataService,
    public feedbackService: FeedbackWrapperService,
    public authService: AuthenticationWrapperService,
  ) {}
}
