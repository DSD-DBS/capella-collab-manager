/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  HTTP_INTERCEPTORS,
  withInterceptorsFromDi,
  provideHttpClient,
} from '@angular/common/http';
import { enableProdMode, importProvidersFrom } from '@angular/core';
import { MatNativeDateModule } from '@angular/material/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideAnimations } from '@angular/platform-browser/animations';
import { ToastrModule } from 'ngx-toastr';
import { BACKEND_URL } from 'src/app/environment';
import { BASE_PATH } from 'src/app/openapi';
import 'zone.js';
import { AppRoutingModule } from './app/app-routing.module';
import { AppComponent } from './app/app.component';
import { AuthInterceptor } from './app/general/auth/http-interceptor/auth.interceptor';
import { ErrorHandlingInterceptor } from './app/general/error-handling/error-handling.interceptor';
import { IconModule } from './app/icon.module';

if (import.meta.env.PROD) {
  enableProdMode();
}

bootstrapApplication(AppComponent, {
  providers: [
    importProvidersFrom(
      AppRoutingModule,
      MatNativeDateModule,
      ToastrModule.forRoot({
        positionClass: 'toast-bottom-left',
        timeOut: 10000,
        extendedTimeOut: 2000,
        maxOpened: 5,
        preventDuplicates: true,
        countDuplicates: true,
        resetTimeoutOnDuplicate: true,
        includeTitleDuplicates: true,
      }),
      IconModule,
    ),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ErrorHandlingInterceptor,
      multi: true,
    },
    provideAnimations(),
    provideHttpClient(withInterceptorsFromDi()),
    {
      provide: BASE_PATH,
      useValue: BACKEND_URL,
    },
  ],
}).catch((err) => console.error(err));
