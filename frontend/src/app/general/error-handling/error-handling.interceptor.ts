/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Observable, pipe, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';

@Injectable({
  providedIn: 'root',
})
export class ErrorHandlingInterceptor implements HttpInterceptor {
  constructor(private toastService: ToastService) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      tap({
        next: () => {},
        error: (err) => {
          if (
            typeof err.error !== 'undefined' &&
            typeof err.error.detail !== 'undefined' &&
            err.error.detail.reason
          ) {
            this.toastService.showError(
              'An error occurred!',
              err.error.detail.reason
            );
          } else if (err.status === 0) {
            this.toastService.showError(
              'Backend not reachable',
              'Please check your internet connection and refresh the page!'
            );
          } else if (err.status !== 404) {
            this.toastService.showError(
              'An error occurred!',
              'Please try again!'
            );
          }
        },
      })
    );
  }
}
