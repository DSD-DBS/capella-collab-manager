/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class PageLayoutService {
  showHeader = true;
  showFooter = true;
  showNotice = true;

  disableAll() {
    this.showHeader = false;
    this.showFooter = false;
    this.showNotice = false;
  }

  enableAll() {
    this.showHeader = true;
    this.showFooter = true;
    this.showNotice = true;
  }
}
