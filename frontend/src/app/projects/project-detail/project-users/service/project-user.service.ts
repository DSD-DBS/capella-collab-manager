/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { User } from 'src/app/services/user/user.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectUserService {
  constructor(private http: HttpClient) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';

  PERMISSIONS = { read: 'Read only', write: 'Read/Write' };
  ROLES = { user: 'User', manager: 'Manager' };
  ADVANCED_ROLES = { administrator: 'Administrator', ...this.ROLES };

  projectUser = new BehaviorSubject<ProjectUser | undefined>(undefined);

  verifyRole(requiredRole: ProjectUserRole): boolean {
    if (!this.projectUser.value) {
      return false;
    }

    const roles = ['user', 'manager', 'administrator'];
    return (
      roles.indexOf(requiredRole) <= roles.indexOf(this.projectUser.value.role)
    );
  }

  verifyPermission(requiredPermission: ProjectUserPermission): boolean {
    if (!this.projectUser.value) {
      return false;
    }
    const permissions = ['read', 'write'];
    return (
      permissions.indexOf(requiredPermission) <=
      permissions.indexOf(this.projectUser.value.permission)
    );
  }

  getOwnProjectUser(projectSlug: string): Observable<ProjectUser> {
    return this.http
      .get<ProjectUser>(
        this.BACKEND_URL_PREFIX + projectSlug + '/users/current'
      )
      .pipe(
        tap((projectUser) => {
          this.projectUser.next(projectUser);
        })
      );
  }

  getProjectUsers(project_slug: string): Observable<ProjectUser[]> {
    return this.http.get<ProjectUser[]>(
      this.BACKEND_URL_PREFIX + project_slug + '/users'
    );
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
