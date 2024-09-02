/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { Session } from 'src/app/openapi';
import { SessionService } from '../service/session.service';

@Component({
  templateUrl: './delete-session-dialog.component.html',
  standalone: true,
  imports: [MatButton],
})
export class DeleteSessionDialogComponent {
  constructor(
    private sessionService: SessionService,
    public dialogRef: MatDialogRef<DeleteSessionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public sessions: Session[],
  ) {}

  deleteButton = {
    disabled: false,
    text: 'Terminate',
  };

  deleteAllSessions() {
    this.deleteButton.disabled = true;
    this.deleteButton.text = 'Please wait...';
    const requests = [];
    for (const session of this.sessions) {
      requests.push(this.sessionService.deleteSession(session.id));
    }

    forkJoin(requests).subscribe({
      next: () => this.dialogRef.close(),
      error: () => {
        this.deleteButton.disabled = false;
        this.deleteButton.text = 'Failure. Try again.';
      },
    });
  }
}
