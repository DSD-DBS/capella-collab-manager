/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { BehaviorSubject, map } from 'rxjs';
import { Session } from 'src/app/schemes';
import { UserService } from '../../services/user/user.service';

@Injectable({
  providedIn: 'root',
})
export class UserSessionService {
  constructor(private userService: UserService) {}

  private _sessions = new BehaviorSubject<Session[] | undefined>(undefined);

  readonly sessions = this._sessions.asObservable();
  readonly readonlySessions = this.sessions.pipe(
    map((sessions) =>
      sessions?.filter((session) => session.type === 'readonly')
    )
  );
  readonly persistentSessions = this.sessions.pipe(
    map((sessions) =>
      sessions?.filter((session) => session.type === 'persistent')
    )
  );

  loadSessions(): void {
    this.userService.getOwnActiveSessions().subscribe({
      next: (sessions) => this._sessions.next(sessions),
      error: () => this._sessions.next(undefined),
    });
  }
}
