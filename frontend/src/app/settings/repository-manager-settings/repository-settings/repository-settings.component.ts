// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UserService } from 'src/app/services/user/user.service';
import { RepositoryService } from 'src/app/services/repository/repository.service';

@Component({
  selector: 'app-repository-settings',
  templateUrl: './repository-settings.component.html',
  styleUrls: ['./repository-settings.component.css'],
})
export class RepositorySettingsComponent implements OnInit {
  repository: string = '';
  user_role: string = '';

  constructor(
    private route: ActivatedRoute,
    public userService: UserService,
    public repositoryService: RepositoryService
    ) {}

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      this.repository = params['repository'];
      this.setUserRole();
    });
  }

  setUserRole(): void {
    this.userService.getUser(
      this.userService.getUsernameFromLocalStorage()
      ).subscribe((user) => {
        this.user_role = user.role;
      });
  }
}
