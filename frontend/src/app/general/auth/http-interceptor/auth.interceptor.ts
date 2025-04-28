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
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthenticationService } from 'src/app/openapi';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private router = inject(Router);
  private authService = inject(AuthenticationWrapperService);
  private authenticationService = inject(AuthenticationService);

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    request = request.clone({ withCredentials: true });
    return next.handle(request).pipe(
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
      this.authService.redirectURL = this.router.url;
      localStorage.setItem(this.authService.LOGGED_IN_KEY, 'false');
      if (err.error.detail.err_code == 'TOKEN_SIGNATURE_EXPIRED') {
        return this.authenticationService.refreshIdentityToken().pipe(
          switchMap(() => {
            return next.handle(request);
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
    if (err.status === 403 && err.error.detail.err_code == 'USER_BLOCKED') {
      this.router.navigateByUrl('/logout?reason=blocked');
    }
    throw err;
  }
}
