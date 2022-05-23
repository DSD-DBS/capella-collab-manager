// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';
import { Session, SessionUsage } from '../schemes';
import { SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-session-overview',
  templateUrl: './session-overview.component.html',
  styleUrls: ['./session-overview.component.css'],
})
export class SessionOverviewComponent implements OnInit {
  constructor(
    private sessionService: SessionService,
    private dialog: MatDialog
  ) {}

  sessions: Array<Session> = [];
  displayedColumns = [
    'id',
    'user',
    'repository',
    'ports',
    'created_at',
    'docker_state',
    'guacamole_user',
    'last_seen',
    'actions',
  ];

  ngOnInit(): void {
    this.refreshSessions();
  }

  refreshSessions() {
    this.sessionService
      .getCurrentSessions()
      .subscribe((res: Array<Session>) => {
        this.sessions = res;
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
}
