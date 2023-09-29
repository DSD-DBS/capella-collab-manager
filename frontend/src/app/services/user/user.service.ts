/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HistoryEvent } from 'src/app/events/service/events.service';
import { Session } from 'src/app/schemes';
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
    role: UserRole,
    reason: string
  ): Observable<User> {
    return this.http.post<User>(this.BACKEND_URL_PREFIX, {
      name: username,
      role: role,
      reason: reason,
    });
  }

  getUser(user: User): Observable<User> {
    return this.http.get<User>(this.BACKEND_URL_PREFIX + user.id);
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(this.BACKEND_URL_PREFIX + 'current');
  }

  deleteUser(user: User): Observable<void> {
    return this.http.delete<void>(this.BACKEND_URL_PREFIX + user.id);
  }

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.BACKEND_URL_PREFIX);
  }

  getOwnActiveSessions(): Observable<Array<Session>> {
    return this.http.get<Session[]>(
      this.BACKEND_URL_PREFIX + 'current/sessions'
    );
  }

  getUserHistory(user: User): Observable<UserHistory> {
    return this.http.get<UserHistory>(
      this.BACKEND_URL_PREFIX + user.id + '/history'
    );
  }

  updateRoleOfUser(
    user: User,
    role: UserRole,
    reason: string
  ): Observable<User> {
    return this.http.patch<User>(this.BACKEND_URL_PREFIX + user.id + '/roles', {
      role,
      reason,
    });
  }

  validateUserRole(requiredRole: UserRole): boolean {
    if (this.user === undefined) {
      return false;
    }

    if (requiredRole === 'administrator' && this.user.role === 'user') {
      return false;
    }

    return true;
  }
}

export interface User {
  id: number;
  name: string;
  role: UserRole;
}

export type UserRole = 'user' | 'administrator';

export interface UserHistory extends User {
  created: string;
  last_login: string;
  events: HistoryEvent[];
}
