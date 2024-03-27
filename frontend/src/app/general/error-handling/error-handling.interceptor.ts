/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  HttpContext,
  HttpContextToken,
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
import { Message } from 'src/app/openapi';

// Skips the automated error handling.
// When this option is set, the error messages from the backend are not auto-printed as toast message
export const SKIP_ERROR_HANDLING = new HttpContextToken<boolean>(() => false);

// Pass this context to HTTP requests if you want to skip error handling.
export const SKIP_ERROR_HANDLING_CONTEXT = new HttpContext().set(
  SKIP_ERROR_HANDLING,
  true,
);

@Injectable({
  providedIn: 'root',
})
export class ErrorHandlingInterceptor implements HttpInterceptor {
  constructor(private toastService: ToastService) {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler,
  ): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      catchError(this.constructErrorDetailTransformationObservable),
      tap({
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        next: (event: HttpEvent<any>) => {
          if (this.isErrorHandlingSkipped(request)) {
            return;
          }
          if (event.type == HttpEventType.Response) {
            const body = event.body;
            if (body?.errors) {
              for (const error of body.errors) {
                this.toastService.showError(error.title, error.reason);
              }
            }
            const warnings = body?.warnings;
            if (warnings) {
              this.displayWarningInToaster(warnings);
            }
          }
        },
        error: (err) => {
          if (err.error.detail?.err_code == 'token_exp') {
            return;
          }

          if (this.isErrorHandlingSkipped(request)) {
            return;
          }

          if (err.error && err.error.detail) {
            const detail = err.error.detail;
            if (Array.isArray(detail)) {
              // Pydantic errors
              for (const error of detail) {
                let message = error.msg;
                if (error.loc) {
                  message = 'Field ' + error.loc.join(' > ') + ', ' + message;
                }
                this.toastService.showError(
                  getReasonPhrase(err.status),
                  message,
                );
              }
            } else if (detail.reason) {
              // User defined error
              this.toastService.showError('An error occurred!', detail.reason);
            }
          } else if (err.status === 0) {
            this.toastService.showError(
              'Backend not reachable',
              'Please check your internet connection and refresh the page!',
            );
          } else {
            const warnings = err.error?.warnings;
            if (warnings) {
              this.displayWarningInToaster(warnings);
            } else {
              this.toastService.showError(
                'An error occurred!',
                'Please try again!',
              );
            }
          }
        },
      }),
      // If the body has a payload attribute, map to the attribute
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      map((event: HttpEvent<any>) => {
        if (event.type == HttpEventType.Response) {
          if (event.body?.payload) {
            event = event.clone({ body: event.body.payload });
          }
        }
        return event;
      }),
    );
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  constructErrorDetailTransformationObservable(err: any): Observable<any> {
    // https://github.com/angular/angular/issues/19888

    if (err.error instanceof Blob && err.error.type === 'application/json') {
      return from(
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        new Promise<any>((_resolve, reject) => {
          const reader = new FileReader();
          reader.onload = (e: Event) => {
            try {
              const errmsg = JSON.parse(
                (<FileReaderEventTarget>e.target).result,
              );
              reject(
                new HttpErrorResponse({
                  error: errmsg,
                  headers: err.headers,
                  status: err.status,
                  statusText: err.statusText,
                  url: err.url || undefined,
                }),
              );
            } catch (e) {
              reject(err);
            }
          };
          reader.onerror = () => {
            reject(err);
          };
          reader.readAsText(err.error);
        }),
      );
    }

    throw err;
  }

  private displayWarningInToaster(warnings: Message[]): void {
    for (const warning of warnings) {
      this.toastService.showWarning(warning.title, warning.reason);
    }
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  private isErrorHandlingSkipped(request: HttpRequest<any>) {
    return request.context.get(SKIP_ERROR_HANDLING);
  }
}

export type PayloadWrapper = {
  warnings: Message[];
  errors: Message[];
  payload: unknown;
};

interface FileReaderEventTarget extends EventTarget {
  result: string;
}
