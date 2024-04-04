/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import type { Preview } from '@storybook/angular';
import { setCompodocJson } from '@storybook/addon-docs/angular';
import docJson from '../documentation.json';
import { HttpClientModule } from '@angular/common/http';
import { importProvidersFrom } from '@angular/core';
import { applicationConfig } from '@storybook/angular';
import { ToastrModule } from 'ngx-toastr';
import { RouterModule } from '@angular/router';

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
        importProvidersFrom(HttpClientModule),
        importProvidersFrom(
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
        ),
        importProvidersFrom(RouterModule.forRoot([])),
      ],
    }),
  ],
};

export default preview;
