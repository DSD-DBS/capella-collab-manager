/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { DialogRef } from '@angular/cdk/dialog';
import { HttpClientModule } from '@angular/common/http';
import { importProvidersFrom } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { RouterModule } from '@angular/router';
import { setCompodocJson } from '@storybook/addon-docs/angular';
import type { Preview } from '@storybook/angular';
import { applicationConfig } from '@storybook/angular';
import { ToastrModule } from 'ngx-toastr';
import docJson from '../documentation.json';
import { IconModule } from '../src/app/icon.module';

setCompodocJson(docJson);

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
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
      ],
    }),
  ],
};

export default preview;
