/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import {
  MatButton,
  MatIconAnchor,
  MatIconButton,
} from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
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
    MatCheckbox,
    FormsModule,
    ReactiveFormsModule,
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

  deletionFormGroup = new FormGroup({});

  sessions: Session[] | undefined = undefined;
  displayedColumns = [
    'checkbox',
    'id',
    'user',
    'created_at',
    'preparation_state',
    'state',
    'last_seen',
    'tool',
    'connection_method',
    'type',
    'actions',
  ];

  ngOnInit(): void {
    this.refreshSessions();
  }

  refreshSessions() {
    this.sessionsService.getAllSessions().subscribe((res: Session[]) => {
      this.sessions = res;
      for (const id in this.deletionFormGroup.controls) {
        this.deletionFormGroup.removeControl(id);
      }
      this.sessions.forEach((session: Session) => {
        this.deletionFormGroup.addControl(session.id, new FormControl(false));
      });
    });
  }

  openMultiDeletionDialog(): void {
    const sessions = this.sessions?.filter(
      (session: Session) => this.deletionFormGroup.get(session.id)?.value,
    );

    const dialogRef = this.dialog.open(DeleteSessionDialogComponent, {
      data: sessions,
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

  protected readonly subMinutes = subMinutes;
  protected readonly Date = Date;
  protected readonly GRAFANA_URL = GRAFANA_URL;
}
