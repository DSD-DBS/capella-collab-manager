/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { IntegrationService } from '../integrations/integration.service';
import { NavBarService } from '../navbar/service/nav-bar.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { UserService } from '../services/user/user.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css'],
})
export class SettingsComponent implements OnInit {
  constructor(
    public userService: UserService,
    public projectService: ProjectService,
    private navbarService: NavBarService,
    public integrations: IntegrationService
  ) {
    this.navbarService.title = 'Settings';
  }

  ngOnInit(): void {
    this.userService
      .getUser(this.userService.getUsernameFromLocalStorage())
      .subscribe((res) => {
        this.userService.user = res;
      });

    console.log(this.integrations.t4c);
  }
}
