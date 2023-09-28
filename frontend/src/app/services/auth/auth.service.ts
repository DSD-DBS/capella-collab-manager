/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  _accessToken: string;
  _refreshToken: string;

  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService,
    private cookieService: CookieService
  ) {
    this._accessToken = '';
    this._refreshToken = '';

    if (!environment.production) {
      this._accessToken =
        this.localStorageService.getValue('access_token') || '';
      this._refreshToken =
        this.localStorageService.getValue('refresh_token') || '';
    }
  }

  get accessToken(): string {
    return this._accessToken;
  }

  getRedirectURL(): Observable<GetRedirectURLResponse> {
    return this.http.get<GetRedirectURLResponse>(
      environment.backend_url + '/authentication'
    );
  }

  getAccessToken(code: string, state: string): Observable<PostTokenResponse> {
    return this.http.post<PostTokenResponse>(
      environment.backend_url + '/authentication/tokens',
      {
        code,
        state,
      }
    );
  }

  performTokenRefresh(): Observable<RefreshTokenResponse> {
    return this.http
      .put<PostTokenResponse>(
        environment.backend_url + '/authentication/tokens',
        { refresh_token: this._refreshToken }
      )
      .pipe(
        tap({
          next: (res) => this.logIn(res.access_token, res.refresh_token),
        })
      );
  }

  isLoggedIn(): boolean {
    return !!this._accessToken;
  }

  webSSO() {
    this.getRedirectURL().subscribe((res) => {
      window.location.href = res.auth_url;
    });
  }

  logIn(accessToken: string, refreshToken: string) {
    this._accessToken = accessToken;
    this._refreshToken = refreshToken;
    if (!environment.production) {
      this.localStorageService.setValue('access_token', accessToken);
      this.localStorageService.setValue('refresh_token', refreshToken);
    }
    this.cookieService.put('access_token', accessToken, {
      path: '/prometheus',
      sameSite: 'strict',
    });
    this.cookieService.put('access_token', accessToken, {
      path: '/grafana',
      sameSite: 'strict',
    });
  }

  logOut() {
    this._accessToken = '';
    this._refreshToken = '';
    if (!environment.production) {
      this.localStorageService.setValue('access_token', '');
      this.localStorageService.setValue('refresh_token', '');
    }
    this.localStorageService.setValue('GUAC_AUTH', '');
    this.cookieService.remove('access_token', { path: '/prometheus' });
    return this.http
      .get(environment.backend_url + '/authentication/logout')
      .subscribe();
  }

  cacheCurrentPath(path: string) {
    this.localStorageService.setValue('current_path', path);
  }

  getCurrentPath() {
    const path = this.localStorageService.getValue('current_path');
    this.cacheCurrentPath('');
    return path || '/';
  }
}

export interface GetRedirectURLResponse {
  auth_url: string;
  state: string;
}

export interface PostTokenResponse {
  access_token: string;
  token_type: string;
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  token_type: string;
  refresh_token: string;
}
