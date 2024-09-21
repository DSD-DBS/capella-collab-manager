/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButton, MatIconButton } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatDivider } from '@angular/material/divider';
import {
  MatFormField,
  MatLabel,
  MatSuffix,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatTooltip } from '@angular/material/tooltip';
import { Router, RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { filter, take } from 'rxjs';
import {
  InputDialogComponent,
  InputDialogResult,
} from 'src/app/helpers/input-dialog/input-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Project,
  ProjectUser,
  ProjectUserPermission,
  ProjectUserRole,
  User,
} from 'src/app/openapi';
import { AddUserToProjectDialogComponent } from 'src/app/projects/project-detail/project-users/add-user-to-project/add-user-to-project.component';
import { ProjectAuditLogComponent } from 'src/app/projects/project-detail/project-users/project-audit-log/project-audit-log.component';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-user-settings',
  templateUrl: './project-user-settings.component.html',
  standalone: true,
  imports: [
    MatButton,
    MatIcon,
    MatDivider,
    MatFormField,
    MatLabel,
    MatInput,
    FormsModule,
    MatSuffix,
    RouterLink,
    MatIconButton,
    MatTooltip,
    NgxSkeletonLoaderModule,
    AsyncPipe,
  ],
})
export class ProjectUserSettingsComponent implements OnInit {
  public project?: Project;

  search = '';

  constructor(
    public projectUserService: ProjectUserService,
    public userService: OwnUserWrapperService,
    private toastService: ToastService,
    private projectService: ProjectWrapperService,
    private dialog: MatDialog,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.projectService.project$
      .pipe(filter(Boolean), untilDestroyed(this))
      .subscribe((project) => {
        this.project = project;
      });
  }

  get permissions() {
    return ProjectUserService.PERMISSIONS;
  }

  get advanced_roles() {
    return ProjectUserService.ADVANCED_ROLES;
  }

  get projectUserRoles() {
    return Object.values(ProjectUserRole);
  }

  removeUserFromProject(user: User): void {
    if (!this.project) {
      return;
    }

    const projectName = this.project.name;
    const projectSlug = this.project.slug;

    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: 'Remove User from Project',
        text: `Do you really want to remove '${user.name}' from the project '${projectName}')? Please provide a reason.`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.projectUserService
          .deleteUserFromProject(projectSlug, user.id, result.text)
          .subscribe({
            next: () => {
              this.projectUserService.loadProjectUsers(projectSlug);
              this.toastService.showSuccess(
                `User removed`,
                `User '${user.name}' has been removed from project '${projectName}'`,
              );
            },
          });
      }
    });
  }

  upgradeUserToProjectManager(user: User): void {
    if (!this.project) {
      return;
    }

    const projectName = this.project.name;
    const projectSlug = this.project.slug;

    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: 'Upgrade to Project Manager Role',
        text: `Do you really want to upgrade '${user.name}' to Project Manager in the project '${projectName}'? Please provide a reason.`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.projectUserService
          .changeRoleOfProjectUser(projectSlug, user.id, 'manager', result.text)
          .subscribe({
            next: () =>
              this.toastService.showSuccess(
                `User modified`,
                `User '${user.name}' can now manage the project '${projectName}'`,
              ),
          });
      }
    });
  }

  downgradeUserToUserRole(user: User): void {
    if (!this.project) {
      return;
    }

    const projectName = this.project.name;
    const projectSlug = this.project.slug;

    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: "Downgrade to 'User' Role",
        text: `Do you really want to downgrade '${user.name}' to 'User' in the project '${projectName}'? Please provide a reason.`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.projectUserService
          .changeRoleOfProjectUser(projectSlug, user.id, 'user', result.text)
          .subscribe({
            next: () =>
              this.toastService.showSuccess(
                `User modified`,
                `User '${user.name}' is no longer project administrator in the project '${projectName}'`,
              ),
          });
      }
    });
  }

  setUserPermission(user: User, permission: ProjectUserPermission): void {
    if (!this.project) {
      return;
    }

    const projectName = this.project.name;
    const projectSlug = this.project.slug;

    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: 'Modify Permission',
        text: `Do you really want to set the permission of '${user.name}' to '${permission}' in the project '${projectName}'? Please provide a reason.`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.projectUserService
          .changePermissionOfProjectUser(
            projectSlug,
            user.id,
            permission,
            result.text,
          )
          .subscribe({
            next: () => {
              this.projectUserService.loadProjectUsers(projectSlug);
              this.toastService.showSuccess(
                `User modified`,
                `User '${user.name}' has the permission '${permission}' in the project '${projectName}' now`,
              );
            },
          });
      }
    });
  }

  getProjectUsersByRole(
    projectUsers: ProjectUser[] | undefined | null,
    role: string,
  ): ProjectUser[] | undefined {
    if (projectUsers === undefined || projectUsers === null) {
      return undefined;
    }

    return projectUsers?.filter(
      (pUser) =>
        pUser.role == role &&
        pUser.user.name.toLowerCase().includes(this.search.toLowerCase()),
    );
  }

  openAddUserDialog() {
    this.dialog.open(AddUserToProjectDialogComponent, {
      data: { project: this.project },
    });
  }

  openAuditLogDialog() {
    this.projectService.project$.pipe(take(1)).subscribe((project) => {
      this.dialog.open(ProjectAuditLogComponent, {
        data: {
          projectSlug: project?.slug,
        },
      });
    });
  }

  hasRoute(route: string): boolean {
    return this.router.url.includes(route);
  }

  isInProjectCreation(): boolean {
    return this.hasRoute('projects/create');
  }
}
