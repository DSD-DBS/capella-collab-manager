/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
  private _tokens = new BehaviorSubject<Token[] | undefined>(undefined);

  readonly tokens$ = this._tokens.asObservable();

  loadTokens(): void {
    this.http
      .get<Token[]>(environment.backend_url + '/users/current/tokens')
      .subscribe({
        next: (token) => this._tokens.next(token),
        error: () => this._tokens.next(undefined),
      });
  }

  createToken(
    description: string,
    expiration_date: Date,
    source: string,
  ): Observable<CreateTokenResponse> {
    return this.http
      .post<CreateTokenResponse>(
        environment.backend_url + `/users/current/tokens`,
        {
          description,
          expiration_date,
          source,
        },
      )
      .pipe(tap(() => this.loadTokens()));
  }

  deleteToken(token: Token): Observable<void> {
    return this.http
      .delete<void>(
        environment.backend_url + `/users/current/tokens/${token.id}`,
      )
      .pipe(tap(() => this.loadTokens()));
  }
}

export type Token = {
  description: string;
  expiration_date: string;
  source: string;
  id: number;
};

export type CreateTokenResponse = Token & {
  password: string;
};
