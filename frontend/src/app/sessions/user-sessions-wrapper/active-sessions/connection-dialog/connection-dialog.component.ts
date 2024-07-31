/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Session,
  SessionConnectionInformation,
  SessionsService,
} from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';
import {
  SessionService,
  isPersistentSession,
} from 'src/app/sessions/service/session.service';
import { DisplayValueComponent } from '../../../../helpers/display-value/display-value.component';

@Component({
  selector: 'app-connection-dialog',
  templateUrl: './connection-dialog.component.html',
  styleUrls: ['./connection-dialog.component.css'],
  standalone: true,
  imports: [DisplayValueComponent, MatButton],
})
export class ConnectionDialogComponent {
  isPersistentSessionAlias = isPersistentSession;

  connectionInfo?: SessionConnectionInformation = undefined;

  constructor(
    public userService: UserWrapperService,
    private sessionService: SessionService,
    private sessionsService: SessionsService,
    @Inject(MAT_DIALOG_DATA) public session: Session,
    public dialogRef: MatDialogRef<ConnectionDialogComponent>,
    private toastService: ToastService,
  ) {
    this.sessionsService
      .getSessionConnectionInformation(this.session.id)
      .subscribe((connectionInfo) => {
        this.connectionInfo = connectionInfo.payload;
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
    this.sessionService.setConnectionInformation(this.connectionInfo);
    if (this.connectionInfo.redirect_url) {
      window.open(this.connectionInfo.redirect_url);
    } else {
      this.toastService.showError(
        "Couldn't connect to session.",
        'No redirect URL was found. Please contact your administrator.',
      );
    }
  }
}
