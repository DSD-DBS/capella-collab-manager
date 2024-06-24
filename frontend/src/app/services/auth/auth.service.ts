/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  SESSION_STORAGE_NONCE_KEY = 'nonce';
  SESSION_STORAGE_CODE_VERIFIER_KEY = 'coderVerifier';
  LOGGED_IN_KEY = 'loggedIn';

  constructor(private http: HttpClient) {}

  getRedirectURL(): Observable<GetRedirectURLResponse> {
    return this.http.get<GetRedirectURLResponse>(
      environment.backend_url + '/authentication',
    );
  }

  getIdentityToken(
    code: string,
    nonce: string,
    code_verifier: string,
  ): Observable<void> {
    return this.http.post<void>(
      environment.backend_url + '/authentication/tokens',
      {
        code,
        nonce,
        code_verifier,
      },
    );
  }

  performTokenRefresh(): Observable<void> {
    return this.http.put<void>(
      environment.backend_url + '/authentication/tokens',
      {},
    );
  }

  isLoggedIn(): boolean {
    const loggedIn = localStorage.getItem(this.LOGGED_IN_KEY);
    return loggedIn !== null && loggedIn === 'true';
  }

  login(redirectTo: string) {
    this.getRedirectURL().subscribe((res) => {
      sessionStorage.setItem(res.state, redirectTo);
      sessionStorage.setItem(this.SESSION_STORAGE_NONCE_KEY, res.nonce);
      sessionStorage.setItem(
        this.SESSION_STORAGE_CODE_VERIFIER_KEY,
        res.code_verifier,
      );
      window.location.href = res.auth_url;
    });
  }

  logOut() {
    localStorage.setItem('GUAC_AUTH', '');
    localStorage.setItem(this.LOGGED_IN_KEY, 'false');
    return this.http
      .delete(environment.backend_url + '/authentication/tokens')
      .subscribe();
  }
}

export interface GetRedirectURLResponse {
  auth_url: string;
  state: string;
  nonce: string;
  code_verifier: string;
}
