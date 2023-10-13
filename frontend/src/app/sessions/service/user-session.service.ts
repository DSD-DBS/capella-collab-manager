/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { BehaviorSubject, map, filter } from 'rxjs';
import {
  isPersistentSession,
  isReadonlySession,
  Session,
} from 'src/app/schemes';
import { UserService } from '../../services/user/user.service';

@Injectable({
  providedIn: 'root',
})
export class UserSessionService {
  constructor(private userService: UserService) {}

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
    this.userService.getOwnActiveSessions().subscribe({
      next: (sessions) => this._sessions.next(sessions),
      error: () => this._sessions.next(undefined),
    });
  }
}
