/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
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
import { User } from 'src/app/openapi';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectUserService {
  constructor(
    private http: HttpClient,
    private projectService: ProjectWrapperService,
  ) {
    this.resetProjectUserOnProjectReset();
    this.resetProjectUsersOnProjectReset();
    this.loadProjectUsersOnProjectChange();
    this.loadProjectUserOnProjectChange();
  }
  BACKEND_URL_PREFIX = environment.backend_url + '/projects';

  PERMISSIONS = { read: 'read only', write: 'read & write' };
  ROLES = { user: 'User', manager: 'Manager' };
  ADVANCED_ROLES = { administrator: 'Administrator', ...this.ROLES };

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

  resetProjectUserOnProjectReset() {
    this.projectService.project$
      .pipe(
        filter((project) => project === undefined),
        tap(() => {
          this._projectUser.next(undefined);
        }),
      )
      .subscribe();
  }

  resetProjectUsersOnProjectReset() {
    this.projectService.project$
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
    this.projectService.project$
      .pipe(
        filter(Boolean),
        switchMap((project) =>
          this.http.get<ProjectUser>(
            `${this.BACKEND_URL_PREFIX}/${project.slug}/users/current`,
          ),
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
      this.projectService.project$.pipe(filter(Boolean)),
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
    this.http
      .get<ProjectUser[]>(`${this.BACKEND_URL_PREFIX}/${projectSlug}/users`)
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
    permission: string,
    reason: string,
  ): Observable<ProjectUser> {
    return this.http
      .post<ProjectUser>(`${this.BACKEND_URL_PREFIX}/${projectSlug}/users`, {
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
    return this.http
      .patch<null>(
        `${this.BACKEND_URL_PREFIX}/${projectSlug}/users/${userID}`,
        {
          role,
          reason,
        },
      )
      .pipe(tap(() => this.loadProjectUsers(projectSlug)));
  }

  changePermissionOfProjectUser(
    projectSlug: string,
    userID: number,
    permission: ProjectUserPermission,
    reason: string,
  ): Observable<null> {
    return this.http.patch<null>(
      `${this.BACKEND_URL_PREFIX}/${projectSlug}/users/${userID}`,
      { permission, reason },
    );
  }

  deleteUserFromProject(
    projectSlug: string,
    userID: number,
    reason: string,
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.BACKEND_URL_PREFIX}/${projectSlug}/users/${userID}`,
      { body: reason },
    );
  }
}

export type ProjectUser = {
  project_name: string;
  permission: ProjectUserPermission;
  role: ProjectUserRole;
  user: User;
};

export type ProjectUserPermission = 'read' | 'write';
export type ProjectUserRole = 'user' | 'manager' | 'administrator';
export type SimpleProjectUserRole = 'user' | 'manager';
