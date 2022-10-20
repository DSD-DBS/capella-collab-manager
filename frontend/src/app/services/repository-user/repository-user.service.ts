/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ProjectUser } from 'src/app/schemes';
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

  getRepoUsers(repository: string): Observable<ProjectUser[]> {
    return this.http.get<ProjectUser[]>(
      this.BACKEND_URL_PREFIX + repository + '/users'
    );
  }

  addUserToRepo(
    repository: string,
    username: string,
    role: 'user' | 'manager',
    permission: string
  ): Observable<ProjectUser> {
    return this.http.post<ProjectUser>(
      this.BACKEND_URL_PREFIX + repository + '/users',
      { username, role, permission }
    );
  }

  changeRoleOfRepoUser(
    repository: string,
    userID: number,
    role: 'user' | 'manager'
  ): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + userID,
      { role }
    );
  }

  updatePasswordOfUser(
    repository: string,
    userID: number,
    password: string
  ): Observable<void> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + userID,
      { password }
    );
  }

  changePermissionOfRepoUser(
    repository: string,
    userID: number,
    permission: 'read' | 'write'
  ): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + userID,
      { permission }
    );
  }

  deleteUserFromRepo(repository: string, userID: number): Observable<any> {
    return this.http.delete<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + userID
    );
  }
}
