/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import {
  BehaviorSubject,
  map,
  filter,
  switchMap,
  tap,
  Observable,
  catchError,
  of,
} from 'rxjs';
import { Session, UsersSessionsService } from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import {
  isPersistentSession,
  isReadonlySession,
} from 'src/app/sessions/service/session.service';

@Injectable({
  providedIn: 'root',
})
export class UserSessionService {
  private usersSessionsService = inject(UsersSessionsService);
  private userWrapperService = inject(OwnUserWrapperService);

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
    this.loadSessionsObservable().subscribe();
  }

  loadSessionsObservable(): Observable<Session[] | undefined> {
    return this.userWrapperService.user$.pipe(
      filter(Boolean),
      switchMap((user) =>
        this.usersSessionsService.getSessionsForUser(user.id),
      ),
      tap((sessions) => this._sessions.next(sessions)),
      catchError(() => {
        this._sessions.next(undefined);
        return of(undefined);
      }),
    );
  }
}
