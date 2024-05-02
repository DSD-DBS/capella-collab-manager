/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { BehaviorSubject, map, filter, switchMap } from 'rxjs';
import { Session, UsersService } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';
import {
  isPersistentSession,
  isReadonlySession,
} from 'src/app/sessions/service/session.service';

@Injectable({
  providedIn: 'root',
})
export class UserSessionService {
  constructor(
    private usersService: UsersService,
    private userWrapperService: UserWrapperService,
  ) {}

  private _sessions = new BehaviorSubject<Session[] | undefined>(undefined);

  public readonly sessions$ = this._sessions.asObservable();
  public readonly readonlySessions$ = this.sessions$.pipe(
    filter(Boolean),
    map((sessions) => sessions.filter(isReadonlySession)),
  );
  public readonly persistentSessions$ = this.sessions$.pipe(
    filter(Boolean),
    map((sessions) => sessions.filter(isPersistentSession)),
  );

  loadSessions(): void {
    this.userWrapperService.user$
      .pipe(
        filter(Boolean),
        switchMap((user) => this.usersService.getSessionsForUser(user.id)),
      )
      .subscribe({
        next: (sessions) => this._sessions.next(sessions),
        error: () => this._sessions.next(undefined),
      });
  }
}
