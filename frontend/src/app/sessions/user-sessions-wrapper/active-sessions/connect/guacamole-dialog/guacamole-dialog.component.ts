/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Session, isPersistentSession } from 'src/app/schemes';
import { GuacamoleService } from 'src/app/services/guacamole/guacamole.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-guacamole-dialog',
  templateUrl: './guacamole-dialog.component.html',
  styleUrls: ['./guacamole-dialog.component.css'],
})
export class GuacamoleDialogComponent {
  isPersistentSession = isPersistentSession;

  t4cPasswordRevealed = false;

  constructor(
    public userService: UserService,
    private localStorageService: LocalStorageService,
    private guacamoleService: GuacamoleService,
    @Inject(MAT_DIALOG_DATA) public session: Session,
    public dialogRef: MatDialogRef<GuacamoleDialogComponent>,
    private toastService: ToastService,
  ) {}

  redirectToGuacamole(): void {
    this.guacamoleService
      .getGucamoleToken(this.session?.id)
      .subscribe((res) => {
        this.localStorageService.setValue('GUAC_AUTH', res.token);
        window.open(res.url);
      });
  }

  showClipboardMessage(): void {
    this.toastService.showSuccess(
      'Session token copied',
      'The session token was copied to your clipboard.',
    );
  }
}
