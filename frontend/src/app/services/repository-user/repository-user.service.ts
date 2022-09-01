/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { RepositoryUser } from 'src/app/schemes';
import { environment } from 'src/environments/environment';
import { AuthService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root',
})
export class RepositoryUserService {
  constructor(private http: HttpClient) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';

  PERMISSIONS = { read: 'Read only', write: 'Read/Write' };
  ROLES = { user: 'User', manager: 'Manager' };
  ADVANCED_ROLES = { administrator: 'Administrator', ...this.ROLES };

  getRepoUsers(repository: string): Observable<Array<RepositoryUser>> {
    return this.http.get<Array<RepositoryUser>>(
      this.BACKEND_URL_PREFIX + repository + '/users'
    );
  }

  addUserToRepo(
    repository: string,
    username: string,
    role: 'user' | 'manager',
    permission: string
  ): Observable<RepositoryUser> {
    return this.http.post<RepositoryUser>(
      this.BACKEND_URL_PREFIX + repository + '/users',
      { username, role, permission }
    );
  }

  changeRoleOfRepoUser(
    repository: string,
    username: string,
    role: 'user' | 'manager'
  ): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + username,
      { role }
    );
  }

  updatePasswordOfUser(
    repository: string,
    username: string,
    password: string
  ): Observable<void> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + username,
      { password }
    );
  }

  changePermissionOfRepoUser(
    repository: string,
    username: string,
    permission: 'read' | 'write'
  ): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + username,
      { permission }
    );
  }

  deleteUserFromRepo(repository: string, username: string): Observable<any> {
    return this.http.delete<any>(
      this.BACKEND_URL_PREFIX + repository + '/users/' + username
    );
  }
}
