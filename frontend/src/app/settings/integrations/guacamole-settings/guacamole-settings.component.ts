/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';

@Component({
  selector: 'app-guacamole-settings',
  templateUrl: './guacamole-settings.component.html',
  styleUrls: ['./guacamole-settings.component.css'],
})
export class GuacamoleSettingsComponent {
  constructor(private navbarService: NavBarService) {
    this.navbarService.title = 'Settings / Integrations / Gucamole';
  }
}
