/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgClass, AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatAnchor, MatButton } from '@angular/material/button';
import { MatCardContent } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatProgressBar } from '@angular/material/progress-bar';
import { RouterLink } from '@angular/router';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { BeautifyService } from 'src/app/services/beatify/beautify.service';
import { ConnectionDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/connection-dialog/connection-dialog.component';
import { DeleteSessionDialogComponent } from '../../delete-session-dialog/delete-session-dialog.component';
import {
  Session,
  SessionService,
  isPersistentSession,
  isReadonlySession,
} from '../../service/session.service';
import { UserSessionService } from '../../service/user-session.service';
import { FileBrowserDialogComponent } from './file-browser-dialog/file-browser-dialog.component';

@Component({
  selector: 'app-active-sessions',
  templateUrl: './active-sessions.component.html',
  styleUrls: ['./active-sessions.component.css'],
  standalone: true,
  imports: [
    NgxSkeletonLoaderModule,
    MatAnchor,
    RouterLink,
    MatIcon,
    NgClass,
    MatCardContent,
    MatProgressBar,
    MatButton,
    AsyncPipe,
  ],
})
export class ActiveSessionsComponent {
  isReadonlySession = isReadonlySession;
  isPersistentSession = isPersistentSession;

  constructor(
    public sessionService: SessionService,
    public beautifyService: BeautifyService,
    public userSessionService: UserSessionService,
    private dialog: MatDialog,
  ) {}

  openDeletionDialog(sessions: Session[]): void {
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
    });

    dialogRef.afterClosed().subscribe(() => {
      this.userSessionService.loadSessions();
    });
  }

  openConnectDialog(session: Session): void {
    this.dialog.open(ConnectionDialogComponent, {
      data: session,
    });
  }

  uploadFileDialog(session: Session): void {
    this.dialog.open(FileBrowserDialogComponent, { data: session });
  }
}
