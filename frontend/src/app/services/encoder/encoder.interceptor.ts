/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { DefaultUrlSerializer, UrlSerializer, UrlTree } from '@angular/router';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpParameterCodec,
  HttpParams,
} from '@angular/common/http';
import { Observable } from 'rxjs';

// The HTTPClient removes trailing whitespaces in usernames by default, but they exist.
@Injectable()
export class WhitespaceUrlInterceptor implements HttpInterceptor {
  constructor() {}

  intercept(
    request: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {
    const url = request.url.replace(' ', '%20');
    return next.handle(request.clone({ url }));
  }
}
