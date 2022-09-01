/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { RepositoryUser } from 'src/app/schemes';
import { RepositoryService } from 'src/app/services/repository/repository.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-repository-manager-settings',
  templateUrl: './repository-manager-settings.component.html',
  styleUrls: ['./repository-manager-settings.component.css'],
})
export class RepositoryManagerSettingsComponent implements OnInit {
  constructor(
    public repositoryService: RepositoryService,
    public userService: UserService
  ) {}

  ngOnInit(): void {
    this.repositoryService.refreshRepositories();
  }
}
