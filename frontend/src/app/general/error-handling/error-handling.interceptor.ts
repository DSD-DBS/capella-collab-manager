/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpEventType,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpResponse,
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
        next: (event: HttpEvent<any>) => {
          if (event.type == HttpEventType.Response) {
            const body = event.body;
            if (body.errors) {
              for (let error of body.errors) {
                if (error.reason)
                  if (Array.isArray(error.reason)) {
                    error.reason = error.reason.join(' ');
                  }
                this.toastService.showError(
                  error.title || '',
                  error.reason || ''
                );
              }
            }
            if (body.warnings) {
              for (let warning of body.warnings) {
                if (warning.reason)
                  if (Array.isArray(warning.reason)) {
                    warning.reason = warning.reason.join(' ');
                  }
                this.toastService.showWarning(
                  warning.title || '',
                  warning.reason || ''
                );
              }
            }
          }
        },
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
