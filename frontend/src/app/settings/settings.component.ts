/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { ProjectService } from 'src/app/services/project/project.service';
import { NavBarService } from '../general/navbar/service/nav-bar.service';
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
    private navbarService: NavBarService
  ) {
    this.navbarService.title = 'Settings';
  }

  ngOnInit(): void {
    this.userService.updateOwnUser();
  }
}
