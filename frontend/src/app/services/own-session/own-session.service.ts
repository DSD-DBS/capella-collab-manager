/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { Session } from 'src/app/schemes';
import { UserService } from '../user/user.service';

@Injectable({
  providedIn: 'root',
})
export class OwnSessionService {
  sessions: Array<Session> = [];

  constructor(private userService: UserService) {}

  refreshSessions(): Observable<Array<Session>> {
    return this.userService.getOwnActiveSessions().pipe(
      tap((res: Array<Session>) => {
        this.sessions = res;
      })
    );
  }
}
