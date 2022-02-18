import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpHeaders,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { LocalStorageService } from '../local-storage/local-storage.service';
import { catchError, first, map, tap, switchMap } from 'rxjs/operators';
import { Router } from '@angular/router';
import {
  AuthService,
  RefreshTokenResponse,
} from 'src/app/services/auth/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private localStorageService: LocalStorageService,
    private router: Router,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    const req = this.injectAccessToken(request);
    return next.handle(req).pipe(
      catchError((err) => {
        if (err.status === 401) {
          if (err.error.detail.err_code == 'token_exp') {
            return this.refreshToken().pipe(
              switchMap(() => {
                const req = this.injectAccessToken(request);
                return next.handle(req);
              }),
              catchError(() => {
                this.router.navigateByUrl('/logout?reason=session-expired');
                return throwError(err);
              })
            );
          } else {
            this.router.navigateByUrl('/logout?reason=unauthorized');
          }
        } else if (
          typeof err.error.detail !== 'undefined' &&
          err.error.detail.reason
        ) {
          this.snackBar.open(err.error.detail.reason, 'Ok!');
        } else if (err.status !== 404) {
          this.snackBar.open(
            'An unknown error occurred! If you encounter the problem again, please open an issue on Github!',
            'Ok!'
          );
        }

        return throwError(err);
      })
    );
  }

  injectAccessToken(request: HttpRequest<unknown>): HttpRequest<unknown> {
    let access_token = this.localStorageService.getValue('access_token');
    return request.clone({
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${access_token}`,
      }),
    });
  }

  refreshToken(): Observable<RefreshTokenResponse> {
    console.log('Token is expired. Refreshing token...');
    const refresh_token = this.localStorageService.getValue('refresh_token');

    return this.authService.refreshToken(refresh_token).pipe(
      map((res) => {
        this.localStorageService.setValue('access_token', res.access_token);
        this.localStorageService.setValue('refresh_token', res.refresh_token);
        return res;
      }, first())
    );
  }
}
