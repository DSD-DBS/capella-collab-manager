/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { Subscription } from 'rxjs';
import { BeautifyService } from 'src/app/services/beatify/beautify.service';
import { Session } from '../../schemes';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';
import { SessionService } from '../service/session.service';
import { UserSessionService } from '../service/user-session.service';
import { GuacamoleComponent } from '../session-created/guacamole/guacamole.component';
import { FileBrowserComponent } from './file-browser/file-browser.component';

@Component({
  selector: 'app-active-sessions',
  templateUrl: './active-sessions.component.html',
  styleUrls: ['./active-sessions.component.css'],
})
export class ActiveSessionsComponent implements OnInit, OnDestroy {
  sessions?: Session[] = undefined;
  private sessionsSubscription?: Subscription;

  constructor(
    public sessionService: SessionService,
    public beautifyService: BeautifyService,
    private userSessionService: UserSessionService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.sessionsSubscription = this.userSessionService.sessions.subscribe(
      (sessions) => (this.sessions = sessions)
    );
  }

  ngOnDestroy(): void {
    this.sessionsSubscription?.unsubscribe();
  }

  openDeletionDialog(sessions: Session[]): void {
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
    });

    if (sessions.length) {
    }

    dialogRef.afterClosed().subscribe(() => {
      this.userSessionService.loadSessions();
    });
  }

  openConnectDialog(session: Session): void {
    this.dialog.open(GuacamoleComponent, {
      data: session,
    });
  }

  uploadFileDialog(session: Session): void {
    this.dialog.open(FileBrowserComponent, { data: session });
  }
}
