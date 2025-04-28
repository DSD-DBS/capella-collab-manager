/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Session,
  SessionConnectionInformation,
  SessionsService,
} from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import {
  SessionService,
  isPersistentSession,
} from 'src/app/sessions/service/session.service';
import { DisplayValueComponent } from '../../../../helpers/display-value/display-value.component';

@Component({
  selector: 'app-connection-dialog',
  templateUrl: './connection-dialog.component.html',
  imports: [DisplayValueComponent, MatButton],
})
export class ConnectionDialogComponent {
  userService = inject(OwnUserWrapperService);
  private sessionService = inject(SessionService);
  private sessionsService = inject(SessionsService);
  session = inject<Session>(MAT_DIALOG_DATA);
  dialogRef = inject<MatDialogRef<ConnectionDialogComponent>>(MatDialogRef);
  private toastService = inject(ToastService);

  isPersistentSessionAlias = isPersistentSession;

  connectionInfo?: SessionConnectionInformation = undefined;

  constructor() {
    this.sessionsService
      .getSessionConnectionInformation(this.session.id)
      .subscribe((connectionInfo) => {
        this.connectionInfo = connectionInfo.payload;
      });
  }

  redirectToSession(): void {
    if (!this.connectionInfo) return;
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
