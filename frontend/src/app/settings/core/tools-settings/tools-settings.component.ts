/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';

@Component({
  selector: 'app-dockerimage-settings',
  templateUrl: './tools-settings.component.html',
  styleUrls: ['./tools-settings.component.css'],
})
export class ToolsSettingsComponent implements OnInit {
  constructor(private navbarService: NavBarService) {
    this.navbarService.title = 'Settings / Core / Dockerimages';
  }
}
