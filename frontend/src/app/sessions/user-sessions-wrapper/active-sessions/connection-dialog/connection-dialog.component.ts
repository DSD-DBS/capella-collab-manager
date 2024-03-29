/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { UserService } from 'src/app/services/user/user.service';
import {
  Session,
  SessionConnectionInformation,
  SessionService,
  isPersistentSession,
} from 'src/app/sessions/service/session.service';

@Component({
  selector: 'app-connection-dialog',
  templateUrl: './connection-dialog.component.html',
  styleUrls: ['./connection-dialog.component.css'],
})
export class ConnectionDialogComponent {
  isPersistentSessionAlias = isPersistentSession;

  connectionInfo?: SessionConnectionInformation = undefined;

  constructor(
    public userService: UserService,
    private sessionService: SessionService,
    @Inject(MAT_DIALOG_DATA) public session: Session,
    public dialogRef: MatDialogRef<ConnectionDialogComponent>,
    private toastService: ToastService,
  ) {
    this.sessionService
      .getSessionConnectionInformation(this.session.id)
      .subscribe((connectionInfo) => {
        this.connectionInfo = connectionInfo;
      });
  }

  redirectToSession(): void {
    if (!this.connectionInfo) {
      this.toastService.showError(
        'Session connection information is not available yet.',
        'Try again later.',
      );
      return;
    }
    this.sessionService.setConnectionInformation(
      this.session,
      this.connectionInfo!,
    );
    if (this.connectionInfo.redirect_url) {
      window.open(this.connectionInfo!.redirect_url);
    } else {
      this.toastService.showError(
        "Couldn't connect to session.",
        'No redirect URL was found. Please contact your administrator.',
      );
    }
  }
}
