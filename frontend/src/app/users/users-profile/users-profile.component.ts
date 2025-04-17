/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, DatePipe } from '@angular/common';
import { Component } from '@angular/core';
import { UntilDestroy } from '@ngneat/until-destroy';
import { ChipComponent } from 'src/app/helpers/chip/chip.component';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';
import { UnifiedConfigWrapperService } from '../../services/unified-config-wrapper/unified-config-wrapper.service';
import { BetaTestingComponent } from './beta-testing/beta-testing.component';
import { CommonProjectsComponent } from './common-projects/common-projects.component';
import { ResetHiddenAnnouncementsComponent } from './reset-hidden-announcements/reset-hidden-announcements.component';
import { UserInformationComponent } from './user-information/user-information.component';
import { UserWorkspacesComponent } from './user-workspaces/user-workspaces.component';

@UntilDestroy()
@Component({
  selector: 'app-users-profile',
  templateUrl: './users-profile.component.html',
  imports: [
    DatePipe,
    CommonProjectsComponent,
    UserInformationComponent,
    UserWorkspacesComponent,
    AsyncPipe,
    BetaTestingComponent,
    ResetHiddenAnnouncementsComponent,
    ChipComponent,
  ],
})
export class UsersProfileComponent {
  constructor(
    public ownUserService: OwnUserWrapperService,
    public userWrapperService: UserWrapperService,
    public unifiedConfigWrapperService: UnifiedConfigWrapperService,
  ) {}
}
