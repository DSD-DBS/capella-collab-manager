/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatAnchor, MatButton, MatIconButton } from '@angular/material/button';
import { MatCardContent } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatProgressBar } from '@angular/material/progress-bar';
import { MatTooltip } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { Session } from 'src/app/openapi';
import { BeautifyService } from 'src/app/services/beatify/beautify.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { ConnectionDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/connection-dialog/connection-dialog.component';
import { SessionSharingDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/session-sharing-dialog/session-sharing-dialog.component';
import { DeleteSessionDialogComponent } from '../../delete-session-dialog/delete-session-dialog.component';
import { FeedbackWrapperService } from '../../feedback/feedback.service';
import {
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
    MatIconButton,
    MatTooltip,
  ],
})
export class ActiveSessionsComponent {
  isReadonlySession = isReadonlySession;
  isPersistentSession = isPersistentSession;

  constructor(
    public sessionService: SessionService,
    public beautifyService: BeautifyService,
    public userSessionService: UserSessionService,
    public feedbackService: FeedbackWrapperService,
    private userWrapperService: OwnUserWrapperService,
    private dialog: MatDialog,
  ) {}

  openDeletionDialog(sessions: Session[]): void {
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        if (this.feedbackService.shouldShowPostSessionPrompt()) {
          this.feedbackService.showDialog(
            sessions,
            'After session termination',
          );
        }

        this.userSessionService.loadSessions();
      }
    });
  }

  openConnectDialog(session: Session): void {
    this.dialog.open(ConnectionDialogComponent, {
      data: session,
    });
  }

  openShareDialog(session: Session): void {
    this.dialog.open(SessionSharingDialogComponent, {
      data: session,
    });
  }

  uploadFileDialog(session: Session): void {
    this.dialog.open(FileBrowserDialogComponent, { data: session });
  }

  isSessionShared(session: Session): boolean {
    return session.owner.id != this.userWrapperService.user?.id;
  }
}
