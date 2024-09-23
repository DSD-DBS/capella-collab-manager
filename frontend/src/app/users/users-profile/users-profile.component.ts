/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, DatePipe } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';
import { CommonProjectsComponent } from './common-projects/common-projects.component';
import { UserInformationComponent } from './user-information/user-information.component';
import { UserWorkspacesComponent } from './user-workspaces/user-workspaces.component';

@UntilDestroy()
@Component({
  selector: 'app-users-profile',
  templateUrl: './users-profile.component.html',
  standalone: true,
  imports: [
    RouterLink,
    DatePipe,
    CommonProjectsComponent,
    UserInformationComponent,
    UserWorkspacesComponent,
    AsyncPipe,
  ],
})
export class UsersProfileComponent {
  constructor(
    public ownUserService: OwnUserWrapperService,
    public userWrapperService: UserWrapperService,
  ) {}
}
