/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class PageLayoutService {
  showNavbar = true;
  showFooter = true;
  showAnnouncement = true;

  hideNavbar() {
    this.showNavbar = false;
  }

  enableAll() {
    this.showNavbar = true;
    this.showFooter = true;
    this.showAnnouncement = true;
  }
}
