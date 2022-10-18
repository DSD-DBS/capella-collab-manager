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
    if (this.authService.isLoggedIn()) {
      this.getAndSaveOwnUser();
    }
  }

  getAndSaveOwnUser(): void {
    this.getUser(this.getUserName()).subscribe((res) => {
      this.user = res;
    });
  }

  getUser(username: string): Observable<User> {
    return this.http.get<User>(
      this.BACKEND_URL_PREFIX + encodeURIComponent(username)
    );
  }

  deleteUser(username: string): Observable<any> {
    return this.http.delete<any>(
      this.BACKEND_URL_PREFIX + encodeURIComponent(username)
    );
  }

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.BACKEND_URL_PREFIX);
  }

  getUserName(): string {
    return this.authService.userName;
  }

  getOwnActiveSessions(): Observable<Array<Session>> {
    return this.http.get<Session[]>(
      this.BACKEND_URL_PREFIX +
        encodeURIComponent(this.getUserName()) +
        '/sessions'
    );
  }

  updateRoleOfUser(
    username: string,
    role: 'user' | 'administrator'
  ): Observable<User> {
    console.log(encodeURIComponent(username));
    return this.http.patch<User>(
      this.BACKEND_URL_PREFIX + encodeURIComponent(username) + '/roles',
      {
        role,
      }
    );
  }
}
