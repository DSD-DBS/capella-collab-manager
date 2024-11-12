/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, DatePipe } from '@angular/common';
import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { BehaviorSubject } from 'rxjs';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';
import { BetaConfigurationOutput, UsersService } from '../../openapi';
import { BetaTestingComponent } from './beta-testing/beta-testing.component';
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
    BetaTestingComponent,
  ],
})
export class UsersProfileComponent {
  constructor(
    public ownUserService: OwnUserWrapperService,
    public userWrapperService: UserWrapperService,
    private usersService: UsersService,
  ) {
    this.getBetaConfig();
  }

  readonly betaConfig$ = new BehaviorSubject<
    BetaConfigurationOutput | undefined
  >(undefined);

  getBetaConfig() {
    return this.usersService.getBetaConfig().subscribe((res) => {
      this.betaConfig$.next(res);
    });
  }
}
