/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { AuthenticationService } from 'src/app/openapi';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { UserWrapperService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-auth-redirect',
  templateUrl: './auth-redirect.component.html',
  styleUrls: ['./auth-redirect.component.css'],
})
export class AuthRedirectComponent implements OnInit {
  constructor(
    private route: ActivatedRoute,
    private toastService: ToastService,
    private authService: AuthenticationWrapperService,
    private authenticationService: AuthenticationService,
    private userService: UserWrapperService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      if (params.error) {
        const redirect_url =
          '/auth?' +
          Object.keys(params)
            .map((key) =>
              ['error', 'error_description', 'error_uri'].includes(key)
                ? [key, params[key]].join('=')
                : '',
            )
            .join('&');
        localStorage.setItem(this.authService.LOGGED_IN_KEY, 'false');
        this.router.navigateByUrl(redirect_url);
        return;
      }

      const redirectTo = sessionStorage.getItem(params.state);
      const nonce = sessionStorage.getItem(
        this.authService.SESSION_STORAGE_NONCE_KEY,
      );
      const codeVerifier = sessionStorage.getItem(
        this.authService.SESSION_STORAGE_CODE_VERIFIER_KEY,
      );

      if (nonce === null || codeVerifier === null) {
        this.toastService.showError(
          'Missing nonce or code verifier value',
          'The nonce or code verifier value is missing in the session storage. If you initiated the login yourself, please retry, and if the error persists or you did not initiate the login, please contact your system administrator',
        );
      } else if (redirectTo === null) {
        this.toastService.showError(
          'State mismatch error',
          'The state returned by the authentication server does not match the local state. If you initiated the login yourself, please retry, and if the error persists or you did not initiate the login, please contact your system administrator.',
        );
        this.router.navigateByUrl('/auth');
      } else {
        sessionStorage.removeItem(params.state);
        sessionStorage.removeItem(this.authService.SESSION_STORAGE_NONCE_KEY);
        sessionStorage.removeItem(
          this.authService.SESSION_STORAGE_CODE_VERIFIER_KEY,
        );

        this.authenticationService
          .getIdentityToken({
            code: params.code,
            nonce,
            code_verifier: codeVerifier,
          })
          .subscribe({
            next: () => {
              localStorage.setItem(this.authService.LOGGED_IN_KEY, 'true');
              this.userService.updateOwnUser();
              this.router.navigateByUrl(redirectTo);
            },
            error: () => this.router.navigateByUrl('/auth'),
          });
      }
    });
  }
}
