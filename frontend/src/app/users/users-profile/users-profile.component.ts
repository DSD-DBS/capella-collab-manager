/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { DatePipe } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { filter, map } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { User, UsersService } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';
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
  ],
})
export class UsersProfileComponent implements OnInit, OnDestroy {
  user: User | undefined;

  constructor(
    public userService: UserWrapperService,
    private usersService: UsersService,
    private route: ActivatedRoute,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit() {
    this.route.params
      .pipe(
        filter((params) => params['userId']),
        map((params) => params['userId']),
      )
      .subscribe((userId: number) => {
        this.usersService.getUser(userId).subscribe((user) => {
          this.user = user;
          this.breadcrumbsService.updatePlaceholder({ user: user });
        });
      });
  }

  ngOnDestroy(): void {
    this.breadcrumbsService.updatePlaceholder({ user: undefined });
  }
}
