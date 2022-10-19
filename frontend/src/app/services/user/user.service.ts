/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { Session, User } from 'src/app/schemes';
import { environment } from 'src/environments/environment';
import { AuthService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root',
})
export class UserService {
  user: User | undefined = undefined;

  BACKEND_URL_PREFIX = environment.backend_url + '/users/';

  constructor(private http: HttpClient, private authService: AuthService) {
    this.updateOwnUser();
  }

  updateOwnUser(): void {
    if (this.authService.isLoggedIn()) {
      this.getCurrentUser().subscribe((res) => {
        this.user = res;
      });
    }
  }

  createUser(
    username: string,
    role: 'user' | 'administrator'
  ): Observable<User> {
    return this.http.post<User>(this.BACKEND_URL_PREFIX, {
      name: username,
      role: role,
    });
  }

  getUser(user: User): Observable<User> {
    return this.http.get<User>(this.BACKEND_URL_PREFIX + user.id);
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(this.BACKEND_URL_PREFIX + 'current');
  }

  deleteUser(user: User): Observable<any> {
    return this.http.delete<any>(this.BACKEND_URL_PREFIX + user.id);
  }

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.BACKEND_URL_PREFIX);
  }

  getUserName(): string {
    return this.authService.userName;
  }

  getOwnActiveSessions(): Observable<Array<Session>> {
    return this.http.get<Session[]>(
      this.BACKEND_URL_PREFIX + 'current/sessions'
    );
  }

  updateRoleOfUser(
    user: User,
    role: 'user' | 'administrator'
  ): Observable<User> {
    return this.http.patch<User>(this.BACKEND_URL_PREFIX + user.id + '/roles', {
      role,
    });
  }
}
