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
import { MatButton } from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatDialog } from '@angular/material/dialog';
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
import { subMinutes } from 'date-fns';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { Session, SessionsService } from 'src/app/openapi';
import { RelativeTimeComponent } from '../../general/relative-time/relative-time.component';
import { DeleteSessionDialogComponent } from '../delete-session-dialog/delete-session-dialog.component';

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

  openDeletionDialog(): void {
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
}
