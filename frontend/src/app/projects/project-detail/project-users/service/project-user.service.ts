/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import {
  BehaviorSubject,
  Observable,
  combineLatest,
  filter,
  map,
  switchMap,
  tap,
} from 'rxjs';
import {
  ProjectsService,
  ProjectUser,
  ProjectUserPermission,
  ProjectUserRole,
} from 'src/app/openapi';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@Injectable({
  providedIn: 'root',
})
export class ProjectUserService {
  constructor(
    private projectWrapperService: ProjectWrapperService,
    private projectsService: ProjectsService,
  ) {
    this.resetProjectUserOnProjectReset();
    this.resetProjectUsersOnProjectReset();
    this.loadProjectUsersOnProjectChange();
    this.loadProjectUserOnProjectChange();
  }
  static PERMISSIONS = { read: 'Read only', write: 'Read & Write' };
  static ROLES = { user: 'User', manager: 'Project Administrator' };
  static ADVANCED_ROLES = {
    administrator: 'Administrator',
    ...ProjectUserService.ROLES,
  };

  private _projectUser = new BehaviorSubject<ProjectUser | undefined>(
    undefined,
  );
  public readonly projectUser$ = this._projectUser.asObservable();

  private _projectUsers = new BehaviorSubject<ProjectUser[] | undefined>(
    undefined,
  );
  public readonly projectUsers$ = this._projectUsers.asObservable();

  public readonly nonAdminProjectUsers$ = this._projectUsers
    .asObservable()
    .pipe(
      map((projectUsers) =>
        projectUsers?.filter(
          (projectUser) => projectUser.role !== 'administrator',
        ),
      ),
    );

  private resetProjectUserOnProjectReset() {
    this.projectWrapperService.project$
      .pipe(
        filter((project) => project === undefined),
        tap(() => {
          this._projectUser.next(undefined);
        }),
      )
      .subscribe();
  }

  private resetProjectUsersOnProjectReset() {
    this.projectWrapperService.project$
      .pipe(
        filter((project) => project === undefined),
        tap(() => {
          this._projectUsers.next(undefined);
        }),
      )
      .subscribe();
  }

  verifyRole(requiredRole: ProjectUserRole): boolean {
    if (!this._projectUser.value) {
      return false;
    }

    const roles = ['user', 'manager', 'administrator'];
    return (
      roles.indexOf(requiredRole) <= roles.indexOf(this._projectUser.value.role)
    );
  }

  verifyPermission(requiredPermission: ProjectUserPermission): boolean {
    if (!this._projectUser.value) {
      return false;
    }
    const permissions = ['read', 'write'];
    return (
      permissions.indexOf(requiredPermission) <=
      permissions.indexOf(this._projectUser.value.permission)
    );
  }

  loadProjectUserOnProjectChange(): void {
    this._projectUser.next(undefined);
    this.projectWrapperService.project$
      .pipe(
        filter(Boolean),
        switchMap((project) =>
          this.projectsService.getCurrentProjectUser(project.slug),
        ),
      )
      .pipe(
        tap((projectUser) => {
          this._projectUser.next(projectUser);
        }),
      )
      .subscribe();
  }

  loadProjectUsersOnProjectChange(): void {
    this._projectUsers.next(undefined);
    combineLatest([
      this.projectWrapperService.project$.pipe(filter(Boolean)),
      this.projectUser$.pipe(
        filter(
          (projectUser) =>
            projectUser?.role === 'manager' ||
            projectUser?.role === 'administrator',
        ),
      ),
    ])
      .pipe(filter(Boolean))
      .subscribe(([project, _]) => {
        this.loadProjectUsers(project.slug);
      });
  }

  loadProjectUsers(projectSlug: string): void {
    this._projectUsers.next(undefined);
    this.projectsService
      .getUsersForProject(projectSlug)
      .pipe(
        tap((projectUsers) => {
          this._projectUsers.next(projectUsers);
        }),
      )
      .subscribe();
  }

  addUserToProject(
    projectSlug: string,
    username: string,
    role: SimpleProjectUserRole,
    permission: ProjectUserPermission,
    reason: string,
  ): Observable<ProjectUser> {
    return this.projectsService
      .addUserToProject(projectSlug, {
        username,
        role,
        permission,
        reason,
      })
      .pipe(
        tap(() => {
          this.loadProjectUsers(projectSlug);
        }),
      );
  }

  changeRoleOfProjectUser(
    projectSlug: string,
    userID: number,
    role: SimpleProjectUserRole,
    reason: string,
  ): Observable<null> {
    return this.projectsService
      .updateProjectUser(projectSlug, userID, {
        role,
        reason,
      })
      .pipe(tap(() => this.loadProjectUsers(projectSlug)));
  }

  changePermissionOfProjectUser(
    projectSlug: string,
    userID: number,
    permission: ProjectUserPermission,
    reason: string,
  ): Observable<null> {
    return this.projectsService.updateProjectUser(projectSlug, userID, {
      permission,
      reason,
    });
  }

  deleteUserFromProject(
    projectSlug: string,
    userID: number,
    reason: string,
  ): Observable<void> {
    return this.projectsService.removeUserFromProject(
      projectSlug,
      userID,
      reason,
    );
  }
}

export type SimpleProjectUserRole = 'user' | 'manager';
