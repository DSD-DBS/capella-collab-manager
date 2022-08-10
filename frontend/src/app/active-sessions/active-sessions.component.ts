// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';
import { Session } from '../schemes';
import { BeautifyService } from '../services/beatify/beautify.service';
import { OwnSessionService } from '../services/own-session/own-session.service';
import { SessionService } from '../services/session/session.service';
import { ReconnectDialogComponent } from './reconnect-dialog/reconnect-dialog.component';
import { UploadDialogComponent } from './upload-dialog/upload-dialog.component';

@Component({
  selector: 'app-active-sessions',
  templateUrl: './active-sessions.component.html',
  styleUrls: ['./active-sessions.component.css'],
})
export class ActiveSessionsComponent implements OnInit {
  showSpinner = false;

  constructor(
    public ownSessionService: OwnSessionService,
    private dialog: MatDialog,
    public sessionService: SessionService,
    public beautifyService: BeautifyService
  ) {}

  ngOnInit(): void {
    this.refreshSessions();
  }

  refreshSessions() {
    this.showSpinner = true;
    this.ownSessionService.refreshSessions().subscribe(() => {
      this.showSpinner = false;
    });
  }

  openDeletionDialog(sessions: Array<Session>): void {
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
    });

    dialogRef.afterClosed().subscribe((_) => {
      this.refreshSessions();
    });
  }

  openReconnectDialog(session: Session): void {
    this.dialog.open(ReconnectDialogComponent, {
      data: session,
    });
  }

  uploadFileDialog(session: Session): void {
    this.dialog.open(UploadDialogComponent, { data: session });
  }
}
