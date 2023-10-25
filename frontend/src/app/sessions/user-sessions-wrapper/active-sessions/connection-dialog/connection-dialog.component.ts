/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { switchMap, takeWhile, timer } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Session, isPersistentSession } from 'src/app/schemes';
import { GuacamoleService } from 'src/app/services/guacamole/guacamole.service';
import { UserService } from 'src/app/services/user/user.service';
import {
  SessionRoute,
  SessionService,
} from 'src/app/sessions/service/session.service';

@Component({
  selector: 'app-connection-dialog',
  templateUrl: './connection-dialog.component.html',
  styleUrls: ['./connection-dialog.component.css'],
})
@UntilDestroy()
export class ConnectionDialogComponent {
  isPersistentSession = isPersistentSession;

  nativeClient = false;
  failedPublicRouteRequest = false;

  sessionRoute?: SessionRoute = undefined;

  constructor(
    public userService: UserService,
    private localStorageService: LocalStorageService,
    private guacamoleService: GuacamoleService,
    private sessionService: SessionService,
    @Inject(MAT_DIALOG_DATA) public session: Session,
    public dialogRef: MatDialogRef<ConnectionDialogComponent>,
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

  requestNativeClient(): void {
    this.nativeClient = true;
    this.failedPublicRouteRequest = false;
    this.sessionRoute = undefined;
    this.sessionService.requestPublicSessionRoute(this.session.id).subscribe({
      error: (err) => {
        if (err.status !== 409) this.failedPublicRouteRequest = true;
      },
    });
    timer(0, 2000)
      .pipe(
        untilDestroyed(this),
        takeWhile(
          () => !this.sessionRoute?.host && !this.failedPublicRouteRequest,
        ),
        switchMap(() =>
          this.sessionService.getPublicSessionRoute(this.session.id),
        ),
      )
      .subscribe({
        next: (route) => {
          this.sessionRoute = route[0];
        },
      });
    this.sessionService.getCurrentSessions;
  }
}
