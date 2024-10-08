/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { AuthenticationService } from 'src/app/openapi';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { FeedbackWrapperService } from 'src/app/sessions/feedback/feedback.service';

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
    private userService: OwnUserWrapperService,
    private router: Router,
    private feedbackService: FeedbackWrapperService,
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      // After removal of the query params there is nothing to do.
      if (Object.keys(params).length === 0) return;
      this.router.navigate([], { queryParams: {} });

      const redirectTo = sessionStorage.getItem(params.state);
      if (params.error) {
        this.authService.redirectURL = redirectTo ?? undefined;
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

      const nonce = sessionStorage.getItem(
        this.authService.SESSION_STORAGE_NONCE_KEY,
      );
      const codeVerifier = sessionStorage.getItem(
        this.authService.SESSION_STORAGE_CODE_VERIFIER_KEY,
      );

      if (nonce === null || codeVerifier === null) {
        this.authService.redirectURL = redirectTo ?? undefined;
        this.toastService.showError(
          'Missing nonce or code verifier value',
          'The nonce or code verifier value is missing in the session storage. If you initiated the login yourself, please retry, and if the error persists or you did not initiate the login, please contact your system administrator',
        );
        this.redirectToLogin();
      } else if (redirectTo === null) {
        this.authService.redirectURL = redirectTo ?? undefined;
        this.toastService.showError(
          'State mismatch error',
          'The state returned by the authentication server does not match the local state. If you initiated the login yourself, please retry, and if the error persists or you did not initiate the login, please contact your system administrator.',
        );
        this.redirectToLogin();
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
              this.feedbackService.triggerFeedbackPrompt();

              if (
                redirectTo.startsWith('/auth') ||
                redirectTo.startsWith('/logout')
              ) {
                this.router.navigateByUrl('/');
              } else {
                this.router.navigateByUrl(redirectTo);
              }
            },
            error: () => {
              this.authService.redirectURL = redirectTo ?? undefined;
              this.redirectToLogin();
            },
          });
      }
    });
  }

  redirectToLogin(): void {
    this.router.navigateByUrl('/auth');
  }
}
