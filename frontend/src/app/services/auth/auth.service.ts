/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie';
import { Observable } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService,
    private cookieService: CookieService
  ) {}

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

  refreshToken(refresh_token: string): Observable<RefreshTokenResponse> {
    return this.http.put<PostTokenResponse>(
      environment.backend_url + '/authentication/tokens',
      { refresh_token }
    );
  }

  isLoggedIn(): boolean {
    return !!this.localStorageService.getValue('access_token');
  }

  logOut() {
    this.localStorageService.setValue('access_token', '');
    this.localStorageService.setValue('refresh_token', '');
    this.localStorageService.setValue('GUAC_AUTH', '');
    this.cookieService.remove('access_token', { path: '/prometheus' });
    return this.http
      .get(environment.backend_url + '/authentication/logout')
      .subscribe();
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
