/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, take } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { AddUserToProjectComponent } from 'src/app/projects/project-detail/project-users/add-user-to-project/add-user-to-project.component';
import { ProjectAuditLogComponent } from 'src/app/projects/project-detail/project-users/project-audit-log/project-audit-log.component';
import {
  ProjectUser,
  ProjectUserPermission,
  ProjectUserService,
} from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { User, UserService } from 'src/app/services/user/user.service';
import { Project, ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-user-settings',
  templateUrl: './project-user-settings.component.html',
})
export class ProjectUserSettingsComponent implements OnInit {
  public project?: Project;

  search = '';

  constructor(
    public projectUserService: ProjectUserService,
    public userService: UserService,
    private toastService: ToastService,
    private projectService: ProjectService,
    private matDialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.projectService.project$
      .pipe(filter(Boolean), untilDestroyed(this))
      .subscribe((project) => {
        this.project = project;
      });
  }

  removeUserFromProject(user: User): void {
    const reason = this.getReason();
    if (!reason || !this.project) {
      return;
    }

    this.projectUserService
      .deleteUserFromProject(this.project.slug, user.id, reason)
      .subscribe(() => {
        this.projectUserService.loadProjectUsers(this.project!.slug);
        this.toastService.showSuccess(
          `User removed`,
          `User '${user.name}' has been removed from project '${this.project?.name}'`
        );
      });
  }

  upgradeUserToProjectManager(user: User): void {
    const reason = this.getReason();
    if (!reason || !this.project) {
      return;
    }

    this.projectUserService
      .changeRoleOfProjectUser(this.project.slug, user.id, 'manager', reason)
      .subscribe(() => {
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' can now manage the project '${this.project?.name}'`
        );
      });
  }

  downgradeUserToUserRole(user: User): void {
    const reason = this.getReason();
    if (!reason || !this.project) {
      return;
    }

    this.projectUserService
      .changeRoleOfProjectUser(this.project.slug, user.id, 'user', reason)
      .subscribe(() => {
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' is no longer project lead in the project '${this.project?.name}'`
        );
      });
  }

  setUserPermission(user: User, permission: ProjectUserPermission): void {
    const reason = this.getReason();
    if (!reason || !this.project) {
      return;
    }

    this.projectUserService
      .changePermissionOfProjectUser(
        this.project.slug,
        user.id,
        permission,
        reason
      )
      .subscribe(() => {
        this.projectUserService.loadProjectUsers(this.project!.slug);
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' has the permission '${permission}' in the project '${this.project?.name}' now`
        );
      });
  }

  getReason(): string | undefined {
    const reason = window.prompt('Please enter a reason!');
    if (!reason) {
      this.toastService.showError('Reason missing', 'You must enter a reason!');
      return;
    }
    return reason;
  }

  getProjectUsersByRole(
    projectUsers: ProjectUser[] | undefined | null,
    role: string
  ): ProjectUser[] | undefined {
    if (projectUsers === undefined || projectUsers === null) {
      return undefined;
    }
    return projectUsers?.filter(
      (pUser) =>
        pUser.role == role &&
        pUser.user.name.toLowerCase().includes(this.search.toLowerCase())
    );
  }

  capitalizeFirstLetter(role: string) {
    return role.charAt(0).toUpperCase() + role.slice(1);
  }

  openAddUserDialog() {
    this.matDialog.open(AddUserToProjectComponent);
  }

  openAuditLogDialog() {
    this.projectService.project$.pipe(take(1)).subscribe((project) => {
      this.matDialog.open(ProjectAuditLogComponent, {
        data: {
          projectSlug: project?.slug,
        },
      });
    });
  }
}
