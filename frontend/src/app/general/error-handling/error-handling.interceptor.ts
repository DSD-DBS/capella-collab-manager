/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  HttpErrorResponse,
  HttpEvent,
  HttpEventType,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
} from '@angular/common/http';
import { Injectable } from '@angular/core';
import { getReasonPhrase } from 'http-status-codes';
import { Observable, tap, map, from, catchError } from 'rxjs';
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
      catchError(this.constructErrorDetailTransformationObservable),
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

          if (err.error && err.error.detail) {
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
              if (Array.isArray(detail.reason)) {
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

  constructErrorDetailTransformationObservable(err: any): Observable<any> {
    // https://github.com/angular/angular/issues/19888

    if (err.error instanceof Blob && err.error.type === 'application/json') {
      return from(
        new Promise<any>((resolve, reject) => {
          let reader = new FileReader();
          reader.onload = (e: Event) => {
            try {
              const errmsg = JSON.parse((<any>e.target).result);
              reject(
                new HttpErrorResponse({
                  error: errmsg,
                  headers: err.headers,
                  status: err.status,
                  statusText: err.statusText,
                  url: err.url,
                })
              );
            } catch (e) {
              reject(err);
            }
          };
          reader.onerror = () => {
            reject(err);
          };
          reader.readAsText(err.error);
        })
      );
    }

    throw err;
  }
}
