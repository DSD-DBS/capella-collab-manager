/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, filter, switchMap, tap } from 'rxjs';
import { ProjectService } from 'src/app/projects/service/project.service';
import { User } from 'src/app/services/user/user.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectUserService {
  constructor(
    private http: HttpClient,
    private projectService: ProjectService
  ) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';

  PERMISSIONS = { read: 'read only', write: 'read & write' };
  ROLES = { user: 'User', manager: 'Manager' };
  ADVANCED_ROLES = { administrator: 'Administrator', ...this.ROLES };

  _projectUser = new BehaviorSubject<ProjectUser | undefined>(undefined);
  projectUser = this._projectUser.asObservable();

  _projectUsers = new BehaviorSubject<ProjectUser[] | undefined>(undefined);
  projectUsers = this._projectUsers.asObservable();

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

  getOwnProjectUser(projectSlug: string): Observable<ProjectUser> {
    return this.http
      .get<ProjectUser>(
        this.BACKEND_URL_PREFIX + projectSlug + '/users/current'
      )
      .pipe(
        tap((projectUser) => {
          this._projectUser.next(projectUser);
        })
      );
  }

  loadProjectUsers(): void {
    this._projectUsers.next(undefined);
    this.projectService.project
      .pipe(
        filter(Boolean),
        switchMap((project) =>
          this.http.get<ProjectUser[]>(
            this.BACKEND_URL_PREFIX + project!.slug + '/users'
          )
        ),
        tap((projectUsers) => {
          this._projectUsers.next(projectUsers);
        })
      )
      .subscribe();
  }

  addUserToProject(
    project_slug: string,
    username: string,
    role: SimpleProjectUserRole,
    permission: string,
    reason: string
  ): Observable<ProjectUser> {
    return this.http.post<ProjectUser>(
      this.BACKEND_URL_PREFIX + project_slug + '/users',
      { username, role, permission, reason }
    );
  }

  changeRoleOfProjectUser(
    project_slug: string,
    userID: number,
    role: SimpleProjectUserRole,
    reason: string
  ): Observable<null> {
    return this.http.patch<null>(
      this.BACKEND_URL_PREFIX + project_slug + '/users/' + userID,
      { role, reason }
    );
  }

  updatePasswordOfUser(
    project_slug: string,
    userID: number,
    password: string
  ): Observable<void> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + project_slug + '/users/' + userID,
      { password }
    );
  }

  changePermissionOfProjectUser(
    project_slug: string,
    userID: number,
    permission: ProjectUserPermission,
    reason: string
  ): Observable<null> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + project_slug + '/users/' + userID,
      { permission, reason }
    );
  }

  deleteUserFromProject(
    project_slug: string,
    userID: number,
    reason: string
  ): Observable<void> {
    return this.http.delete<void>(
      this.BACKEND_URL_PREFIX + project_slug + '/users/' + userID,
      { body: reason }
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
