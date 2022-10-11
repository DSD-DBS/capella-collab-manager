/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';
import { NavBarService } from '../../general/navbar/service/nav-bar.service';
import { Session } from '../../schemes';
import { SessionService } from '../../services/session/session.service';

@Component({
  selector: 'app-session-overview',
  templateUrl: './session-overview.component.html',
  styleUrls: ['./session-overview.component.css'],
})
export class SessionOverviewComponent implements OnInit {
  constructor(
    private sessionService: SessionService,
    private dialog: MatDialog,
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Session Overview';
  }

  deletionFormGroup = new FormGroup({});

  sessions: Session[] = [];
  displayedColumns = [
    'checkbox',
    'id',
    'user',
    'repository',
    'ports',
    'created_at',
    'docker_state',
    'guacamole_user',
    'last_seen',
  ];

  ngOnInit(): void {
    this.refreshSessions();
  }

  refreshSessions() {
    this.sessionService.getCurrentSessions().subscribe((res: Session[]) => {
      this.sessions = res;
      for (const id in this.deletionFormGroup.controls) {
        this.deletionFormGroup.removeControl(id);
      }
      this.sessions.forEach((session: Session) => {
        this.deletionFormGroup.addControl(session.id, new FormControl(false));
      });
    });
  }

  openDeletionDialog(): void {
    const sessions: Session[] = this.sessions.filter(
      (session: Session) => this.deletionFormGroup.get(session.id)?.value
    );

    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
    });

    dialogRef.afterClosed().subscribe((_) => {
      this.refreshSessions();
    });
  }

  selectAllSessions(checked: boolean): void {
    for (const id in this.deletionFormGroup.controls) {
      this.deletionFormGroup.get(id)?.setValue(checked);
    }
  }

  getAllSessionsSelected(): boolean {
    for (const id in this.deletionFormGroup.controls) {
      if (!this.deletionFormGroup.get(id)?.value) {
        return false;
      }
    }

    return true;
  }

  getAnySessionSelected(): boolean {
    for (const id in this.deletionFormGroup.controls) {
      if (this.deletionFormGroup.get(id)?.value) {
        return true;
      }
    }

    return false;
  }
}
