/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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
  showLegal = true;

  disableAll() {
    this.showHeader = false;
    this.showFooter = false;
    this.showNotice = false;
    this.showLegal = false;
  }

  enableAll() {
    this.showHeader = true;
    this.showFooter = true;
    this.showNotice = true;
    this.showLegal = true;
  }
}
