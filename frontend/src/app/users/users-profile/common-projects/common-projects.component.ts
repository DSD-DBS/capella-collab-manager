/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit } from '@angular/core';
import { MatDividerModule } from '@angular/material/divider';
import { RouterLink } from '@angular/router';
import { BehaviorSubject, of, switchMap } from 'rxjs';
import { Project, UsersService } from 'src/app/openapi';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';

@Component({
  selector: 'app-common-projects',
  imports: [CommonModule, MatDividerModule, RouterLink],
  templateUrl: './common-projects.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommonProjectsComponent implements OnInit {
  commonProjects = new BehaviorSubject<Project[] | undefined>(undefined);
  public readonly commonProjects$ = this.commonProjects.asObservable();

  constructor(
    public userService: OwnUserWrapperService,
    public userWrapperService: UserWrapperService,
    private usersService: UsersService,
  ) {}

  ngOnInit(): void {
    this.userWrapperService.user$
      .pipe(
        switchMap((user) => {
          if (!user) return of(undefined);
          return this.usersService.getCommonProjects(user.id);
        }),
      )
      .subscribe({
        next: (projects) => this.commonProjects.next(projects),
        error: () => this.commonProjects.next(undefined),
      });
  }
}
