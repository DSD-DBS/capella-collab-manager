/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  HttpErrorResponse,
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import {
  AuthService,
  RefreshTokenResponse,
} from 'src/app/services/auth/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private router: Router,
    private authService: AuthService,
  ) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    const req = this.injectAccessToken(request);
    return next.handle(req).pipe(
      catchError((err: HttpErrorResponse) => {
        return this.handleTokenExpired(err, request, next);
      }),
    );
  }

  handleTokenExpired(
    err: HttpErrorResponse,
    request: HttpRequest<unknown>,
    next: HttpHandler,
  ) {
    if (err.status === 401) {
      if (err.error.detail.err_code == 'TOKEN_SIGNATURE_EXPIRED') {
        return this.refreshToken().pipe(
          switchMap(() => {
            const req = this.injectAccessToken(request);
            return next.handle(req);
          }),
          catchError(() => {
            this.router.navigateByUrl('/logout?reason=session-expired');
            throw err;
          }),
        );
      } else {
        this.router.navigateByUrl('/logout?reason=unauthorized');
      }
    }

    throw err;
  }

  injectAccessToken(request: HttpRequest<unknown>): HttpRequest<unknown> {
    const access_token = this.authService.accessToken;
    return request.clone({
      headers: request.headers.set('Authorization', `Bearer ${access_token}`),
    });
  }

  refreshToken(): Observable<RefreshTokenResponse> {
    return this.authService.performTokenRefresh();
  }
}
