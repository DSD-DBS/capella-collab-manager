/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  HttpEvent,
  HttpEventType,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { getReasonPhrase } from 'http-status-codes';
import { Observable, tap, map } from 'rxjs';
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
            if (body?.errors) {
              for (let error of body.errors) {
                if (error.reason && Array.isArray(error.reason)) {
                  error.reason = error.reason.join(' ');
                }
                this.toastService.showError(
                  error.title || '',
                  error.reason || ''
                );
              }
            }
            if (body?.warnings) {
              for (let warning of body.warnings) {
                if (warning.reason && Array.isArray(warning.reason)) {
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
          if (err.error.detail?.err_code == 'token_exp') {
            return;
          }

          if (
            typeof err.error !== 'undefined' &&
            typeof err.error.detail !== 'undefined'
          ) {
            let detail = err.error.detail;
            if (Array.isArray(detail)) {
              // Pydantic errors
              for (let error of detail) {
                this.toastService.showError(
                  getReasonPhrase(err.status),
                  error.msg
                );
              }
            } else if (detail.reason) {
              if (detail.reason && Array.isArray(detail.reason)) {
                detail.reason = detail.reason.join(' ');
              }
              // User defined error
              this.toastService.showError('An error occurred!', detail.reason);
            }
          } else if (err.status === 0) {
            this.toastService.showError(
              'Backend not reachable',
              'Please check your internet connection and refresh the page!'
            );
          } else {
            this.toastService.showError(
              'An error occurred!',
              'Please try again!'
            );
          }
        },
      }),
      // If the body has a payload attribute, map to the attribute
      map((event: HttpEvent<any>) => {
        if (event.type == HttpEventType.Response) {
          if (event.body?.payload) {
            event = event.clone({ body: event.body.payload });
          }
        }
        return event;
      })
    );
  }
}
