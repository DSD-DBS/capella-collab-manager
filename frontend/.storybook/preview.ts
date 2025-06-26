/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { applicationConfig, type Preview } from '@analogjs/storybook-angular';
import { DialogRef } from '@angular/cdk/dialog';
import { HttpClientModule } from '@angular/common/http';
import { importProvidersFrom } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { ToastrModule } from 'ngx-toastr';
import 'zone.js';
import { IconModule } from '../src/app/icon.module';
import { mockToastServiceProvider } from '../src/storybook/toast';

export const MOBILE_VIEWPORT = {
  width: 420,
  height: 920,
};

export const DESKTOP_VIEWPORT = {
  width: 1920,
  height: 1080,
};

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    screenshot: {
      viewports: {
        desktop: DESKTOP_VIEWPORT,
        mobile: MOBILE_VIEWPORT,
      },
      fullPage: false,
      captureBeyondViewport: false,
    },
  },
  decorators: [
    applicationConfig({
      providers: [
        importProvidersFrom(
          HttpClientModule,
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
          RouterModule.forRoot([]),
          IconModule,
        ),
        importProvidersFrom(BrowserAnimationsModule),
        { provide: MatDialogRef, useValue: {} },
        { provide: DialogRef, useValue: {} },
        mockToastServiceProvider,
      ],
    }),
  ],
};

export default preview;
