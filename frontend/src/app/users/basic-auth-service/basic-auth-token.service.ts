/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import {
  UsersTokenService,
  UserToken,
  UserTokenWithPassword,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class TokenService {
  constructor(private tokenService: UsersTokenService) {}
  private _tokens = new BehaviorSubject<UserToken[] | undefined>(undefined);

  readonly tokens$ = this._tokens.asObservable();

  loadTokens(): void {
    this.tokenService.getAllTokensOfUser().subscribe({
      next: (token) => this._tokens.next(token),
      error: () => this._tokens.next(undefined),
    });
  }

  createToken(
    description: string,
    expiration_date: Date,
    source: string,
  ): Observable<UserTokenWithPassword> {
    return this.tokenService
      .createTokenForUser({
        description,
        expiration_date: expiration_date.toISOString().substring(0, 10),
        source,
      })
      .pipe(tap(() => this.loadTokens()));
  }

  deleteToken(token: UserToken): Observable<void> {
    return this.tokenService
      .deleteTokenForUser(token.id)
      .pipe(tap(() => this.loadTokens()));
  }
}
