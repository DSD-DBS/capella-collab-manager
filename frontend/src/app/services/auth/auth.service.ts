/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { AuthenticationService } from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class AuthenticationWrapperService {
  private authenticationService = inject(AuthenticationService);

  SESSION_STORAGE_NONCE_KEY = 'CCM_NONCE';
  SESSION_STORAGE_CODE_VERIFIER_KEY = 'CCM_CODE_VERIFIER';
  LOGGED_IN_KEY = 'CCM_LOGGED_IN';

  redirectURL: string | undefined = undefined;

  isLoggedIn(): boolean {
    const loggedIn = localStorage.getItem(this.LOGGED_IN_KEY);
    return loggedIn !== null && loggedIn === 'true';
  }

  login() {
    this.authenticationService.getAuthorizationUrl().subscribe((res) => {
      sessionStorage.setItem(res.state, this.redirectURL ?? '/');
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
    this.authenticationService.logout().subscribe();
  }
}
