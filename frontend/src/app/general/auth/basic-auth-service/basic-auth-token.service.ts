/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class TokenService {
  constructor(private http: HttpClient) {}
  private readonly _tokens = new BehaviorSubject<Token[] | undefined>(
    undefined
  );

  readonly tokens$ = this._tokens.asObservable();

  loadTokens(): void {
    this.http
      .get<Token[]>(environment.backend_url + '/users/current/tokens')
      .subscribe({
        next: (token) => this._tokens.next(token),
        error: () => this._tokens.next(undefined),
      });
  }

  createToken(tokenDescription: string): Observable<string> {
    const password = this.http
      .post<string>(
        environment.backend_url + `/users/current/token`,
        tokenDescription
      )
      .pipe(tap(() => this.loadTokens()));

    return password;
  }

  deleteToken(token: Token): Observable<string> {
    return this.http
      .delete<string>(
        environment.backend_url + `/users/current/token/${token.id}`
      )
      .pipe(tap(() => this.loadTokens()));
  }
}

export type Token = {
  description: string;
  expiration_date: string;
  id: number;
};
