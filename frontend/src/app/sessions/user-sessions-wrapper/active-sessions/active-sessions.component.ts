/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import {
  Session,
  isReadonlySession,
  isPersistentSession,
} from 'src/app/schemes';
import { BeautifyService } from 'src/app/services/beatify/beautify.service';
import { ConnectionDialogComponent } from 'src/app/sessions/user-sessions-wrapper/active-sessions/connection-dialog/connection-dialog.component';
import { DeleteSessionDialogComponent } from '../../delete-session-dialog/delete-session-dialog.component';
import { SessionService } from '../../service/session.service';
import { UserSessionService } from '../../service/user-session.service';
import { FileBrowserDialogComponent } from './file-browser-dialog/file-browser-dialog.component';

@Component({
  selector: 'app-active-sessions',
  templateUrl: './active-sessions.component.html',
  styleUrls: ['./active-sessions.component.css'],
})
export class ActiveSessionsComponent {
  isReadonlySession = isReadonlySession;
  isPersistentSession = isPersistentSession;

  sessions?: Session[] = undefined;

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
    if (session.jupyter_uri) {
      window.open(session.jupyter_uri);
    } else {
      this.dialog.open(ConnectionDialogComponent, {
        data: session,
      });
    }
  }

  uploadFileDialog(session: Session): void {
    this.dialog.open(FileBrowserDialogComponent, { data: session });
  }
}
