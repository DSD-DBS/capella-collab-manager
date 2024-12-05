/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, KeyValuePipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatAnchor, MatButtonModule } from '@angular/material/button';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialog } from '@angular/material/dialog';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatIcon } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { RouterLink } from '@angular/router';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { BehaviorSubject, map } from 'rxjs';
import { Session } from 'src/app/openapi';
import { DeleteSessionDialogComponent } from 'src/app/sessions/delete-session-dialog/delete-session-dialog.component';
import { FeedbackWrapperService } from 'src/app/sessions/feedback/feedback.service';
import { SessionCardComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/session-card/session-card.component';
import { SessionService } from '../../service/session.service';
import { UserSessionService } from '../../service/user-session.service';

@Component({
  selector: 'app-active-sessions',
  templateUrl: './active-sessions.component.html',
  imports: [
    NgxSkeletonLoaderModule,
    MatAnchor,
    RouterLink,
    MatIcon,
    AsyncPipe,
    MatCheckboxModule,
    FormsModule,
    KeyValuePipe,
    SessionCardComponent,
    MatButtonModule,
    MatExpansionModule,
    MatProgressBarModule,
  ],
})
export class ActiveSessionsComponent implements OnInit {
  constructor(
    public sessionService: SessionService,
    public userSessionService: UserSessionService,
    private dialog: MatDialog,
    private feedbackService: FeedbackWrapperService,
  ) {}

  sessions = new BehaviorSubject<SessionWithSelection[] | undefined>(undefined);

  readySessions(sessions: SessionWithSelection[]) {
    return sessions.filter(
      (session) =>
        this.sessionService.beautifyState(
          session.preparation_state,
          session.state,
        ).success,
    );
  }

  // groupBy is not supported by our target browsers
  sessionsGroupedByName = this.sessions.pipe(
    map((sessions) =>
      sessions?.reduce((rv: GroupedSessions, x) => {
        const projectID = x.project?.id ?? -1;
        if (!rv[projectID]) rv[projectID] = [];
        rv[projectID].push(x);
        return rv;
      }, {}),
    ),
  );

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

  openTerminationDialog(sessions: Session[]): void {
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

  get selectedSessionIDs$() {
    return this.sessions.pipe(
      map((sessions) =>
        sessions
          ?.filter((session) => session.selected)
          .map((session) => session.id),
      ),
    );
  }

  sessionIDsForSessions(sessions: SessionWithSelection[]) {
    return sessions.map((session) => session.id);
  }
}

export type SessionWithSelection = Session & { selected: boolean };
type GroupedSessions = Record<number, SessionWithSelection[]>;
