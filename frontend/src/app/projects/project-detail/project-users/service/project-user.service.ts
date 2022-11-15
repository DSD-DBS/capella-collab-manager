/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
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

  getProjectUsers(project_slug: string): Observable<ProjectUser[]> {
    return this.http.get<ProjectUser[]>(
      this.BACKEND_URL_PREFIX + project_slug + '/users'
    );
  }

  addUserToProject(
    project_slug: string,
    username: string,
    role: 'user' | 'manager',
    permission: string
  ): Observable<ProjectUser> {
    return this.http.post<ProjectUser>(
      this.BACKEND_URL_PREFIX + project_slug + '/users',
      { username, role, permission }
    );
  }

  changeRoleOfProjectUser(
    project_slug: string,
    userID: number,
    role: 'user' | 'manager'
  ): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + project_slug + '/users/' + userID,
      { role }
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
    permission: 'read' | 'write'
  ): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + project_slug + '/users/' + userID,
      { permission }
    );
  }

  deleteUserFromProject(project_slug: string, userID: number): Observable<any> {
    return this.http.delete<any>(
      this.BACKEND_URL_PREFIX + project_slug + '/users/' + userID
    );
  }
}

export type ProjectUser = {
  project_name: string;
  permission: 'read' | 'write';
  role: 'user' | 'manager' | 'administrator';
  user: User;
};
