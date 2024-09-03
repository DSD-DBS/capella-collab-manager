/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { MatDividerModule } from '@angular/material/divider';
import { RouterLink } from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { Project, User, UsersService } from 'src/app/openapi';
import { UserWrapperService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-common-projects',
  standalone: true,
  imports: [CommonModule, MatDividerModule, RouterLink],
  templateUrl: './common-projects.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CommonProjectsComponent {
  _user: User | undefined;

  @Input()
  set user(value: User | undefined) {
    this._user = value;
    if (value && value.id !== this.userService.user?.id) {
      this.usersService.getCommonProjects(value.id).subscribe({
        next: (projects) => this.commonProjects.next(projects),
        error: () => this.commonProjects.next(undefined),
      });
    }
  }

  get user(): User | undefined {
    return this._user;
  }

  commonProjects = new BehaviorSubject<Project[] | undefined>(undefined);
  public readonly commonProjects$ = this.commonProjects.asObservable();

  constructor(
    public userService: UserWrapperService,
    private usersService: UsersService,
  ) {}
}
