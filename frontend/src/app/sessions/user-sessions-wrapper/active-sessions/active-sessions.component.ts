/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatAnchor, MatButton, MatIconButton } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { addMinutes, differenceInMinutes } from 'date-fns';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { BehaviorSubject, map } from 'rxjs';
import { Session } from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { ConnectionDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/connection-dialog/connection-dialog.component';
import { SessionSharingDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/session-sharing-dialog/session-sharing-dialog.component';
import { RelativeTimeComponent } from '../../../general/relative-time/relative-time.component';
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
  imports: [
    NgxSkeletonLoaderModule,
    MatAnchor,
    RouterLink,
    MatIcon,
    NgClass,
    MatButton,
    AsyncPipe,
    MatIconButton,
    MatTooltip,
    MatCheckboxModule,
    FormsModule,
    RelativeTimeComponent,
  ],
})
export class ActiveSessionsComponent implements OnInit {
  isReadonlySession = isReadonlySession;
  isPersistentSession = isPersistentSession;

  constructor(
    public sessionService: SessionService,
    public userSessionService: UserSessionService,
    public feedbackService: FeedbackWrapperService,
    private userWrapperService: OwnUserWrapperService,
    private dialog: MatDialog,
  ) {}

  sessions = new BehaviorSubject<SessionWithSelection[] | undefined>(undefined);

  ngOnInit(): void {
    this.userSessionService.sessions$.subscribe((sessions) => {
      const unselectedSessionIDs = new Set(
        this.sessions.value?.filter((s) => !s.selected).map((s) => s.id) ?? [],
      );

      this.sessions.next(
        sessions?.map((s) => ({
          ...s,
          selected: !unselectedSessionIDs.has(s.id),
        })),
      );
    });
  }

  get selectedSessionIDs$() {
    return this.sessions.pipe(
      map((sessions) =>
        sessions
          ?.filter((session) => session.selected)
          .map((session) => session.id),
      ),
    );
  }

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

  minutesUntilSessionTermination(session: Session): number | null {
    if (session.idle_state.available) {
      if (session.idle_state.idle_for_minutes === -1) {
        // session was never connected to, use creation time
        return (
          session.idle_state.terminate_after_minutes -
          differenceInMinutes(session.created_at, Date.now())
        );
      } else {
        return (
          session.idle_state.terminate_after_minutes -
          session.idle_state.idle_for_minutes!
        );
      }
    } else {
      return null;
    }
  }

  protected readonly Date = Date;
  protected readonly addMinutes = addMinutes;
  protected readonly differenceInMinutes = differenceInMinutes;
}

type SessionWithSelection = Session & { selected: boolean };
