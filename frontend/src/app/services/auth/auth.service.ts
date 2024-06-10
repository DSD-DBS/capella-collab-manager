/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(
    private http: HttpClient,
    private localStorageService: LocalStorageService,
  ) {}

  getRedirectURL(): Observable<GetRedirectURLResponse> {
    return this.http.get<GetRedirectURLResponse>(
      environment.backend_url + '/authentication',
    );
  }

  getAccessToken(code: string): Observable<boolean> {
    return this.http
      .post<boolean>(environment.backend_url + '/authentication/tokens', {
        code,
      })
      .pipe(
        tap((_) => {
          this.localStorageService.setValue('loggedIn', 'true');
        }),
      );
  }

  performTokenRefresh(): Observable<boolean> {
    return this.http.put<boolean>(
      environment.backend_url + '/authentication/tokens',
      {},
    );
  }

  isLoggedIn(): boolean {
    return this.localStorageService.getValue('loggedIn') === 'true';
  }

  login(redirectTo: string) {
    this.getRedirectURL().subscribe((res) => {
      sessionStorage.setItem(res.state, redirectTo);
      window.location.href = res.auth_url;
    });
  }

  logOut() {
    this.localStorageService.setValue('GUAC_AUTH', '');
    this.localStorageService.setValue('loggedIn', '');
    return this.http
      .delete(environment.backend_url + '/authentication/tokens')
      .subscribe();
  }
}

export interface GetRedirectURLResponse {
  auth_url: string;
  state: string;
}
