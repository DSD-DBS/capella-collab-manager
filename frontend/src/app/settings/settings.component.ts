/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { RepositoryService } from '../services/repository/repository.service';
import { UserService } from '../services/user/user.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.css'],
})
export class SettingsComponent implements OnInit {
  constructor(
    public userService: UserService,
    public repositoryService: RepositoryService
  ) {}

  ngOnInit(): void {
    this.userService
      .getUser(this.userService.getUserName())
      .subscribe((res) => {
        this.userService.user = res;
      });
  }
}
