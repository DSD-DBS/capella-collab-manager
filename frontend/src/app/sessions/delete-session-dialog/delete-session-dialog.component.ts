/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { forkJoin } from 'rxjs';
import { SessionsService } from 'src/app/openapi';

@Component({
  templateUrl: './delete-session-dialog.component.html',
  imports: [MatButton],
})
export class DeleteSessionDialogComponent {
  private sessionsService = inject(SessionsService);
  dialogRef = inject<MatDialogRef<DeleteSessionDialogComponent>>(MatDialogRef);
  sessions = inject(MAT_DIALOG_DATA);

  deleteButton = {
    disabled: false,
    text: 'Terminate',
  };

  deleteAllSessions() {
    this.deleteButton.disabled = true;
    this.deleteButton.text = 'Please wait...';
    const requests = [];
    for (const session of this.sessions) {
      requests.push(this.sessionsService.terminateSession(session.id));
    }

    forkJoin(requests).subscribe({
      next: () => this.dialogRef.close(true),
      error: () => {
        this.deleteButton.disabled = false;
        this.deleteButton.text = 'Failure. Try again.';
      },
    });
  }
}
