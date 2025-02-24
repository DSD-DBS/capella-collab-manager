/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit } from '@angular/core';
import {
  MatButton,
  MatIconAnchor,
  MatIconButton,
} from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import {
  MatTable,
  MatColumnDef,
  MatHeaderCellDef,
  MatHeaderCell,
  MatCellDef,
  MatCell,
  MatHeaderRowDef,
  MatHeaderRow,
  MatRowDef,
  MatRow,
} from '@angular/material/table';
import { MatTooltip } from '@angular/material/tooltip';
import { subMinutes } from 'date-fns';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { Session, SessionsService } from 'src/app/openapi';
import { GRAFANA_URL } from '../../environment';
import { RelativeTimeComponent } from '../../general/relative-time/relative-time.component';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';
import { ConnectionDialogComponent } from '../user-sessions-wrapper/active-sessions/connection-dialog/connection-dialog.component';

@Component({
  selector: 'app-session-overview',
  templateUrl: './session-overview.component.html',
  imports: [
    MatTable,
    MatColumnDef,
    MatHeaderCellDef,
    MatHeaderCell,
    MatCellDef,
    MatCell,
    MatHeaderRowDef,
    MatHeaderRow,
    MatRowDef,
    MatRow,
    MatButton,
    NgxSkeletonLoaderModule,
    RelativeTimeComponent,
    MatIcon,
    MatTooltip,
    MatIconButton,
    MatIconAnchor,
  ],
})
export class SessionOverviewComponent implements OnInit {
  constructor(
    private sessionsService: SessionsService,
    private dialog: MatDialog,
  ) {}

  sessions: Session[] | undefined = undefined;
  displayedColumns = [
    'id',
    'user',
    'created_at',
    'preparation_state',
    'state',
    'last_seen',
    'tool',
    'type',
    'actions',
  ];

  ngOnInit(): void {
    this.refreshSessions();
  }

  refreshSessions() {
    this.sessionsService.getAllSessions().subscribe((res: Session[]) => {
      this.sessions = res;
    });
  }

  openMultiDeletionDialog(): void {
    if (!this.sessions) return;
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: this.sessions,
    });

    dialogRef.afterClosed().subscribe((_) => {
      this.refreshSessions();
    });
  }

  openSingleDeletionDialog(session: Session): void {
    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: [session],
    });

    dialogRef.afterClosed().subscribe((_) => {
      this.refreshSessions();
    });
  }

  openConnectDialog(session: Session): void {
    this.dialog.open(ConnectionDialogComponent, {
      data: session,
    });
  }

  protected readonly subMinutes = subMinutes;
  protected readonly Date = Date;
  protected readonly GRAFANA_URL = GRAFANA_URL;
}
