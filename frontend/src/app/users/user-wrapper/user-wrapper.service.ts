/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { User, UsersService } from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class UserWrapperService {
  private userService = inject(UsersService);

  _user = new BehaviorSubject<User | undefined>(undefined);
  user$ = this._user.asObservable();

  private _users = new BehaviorSubject<User[] | undefined>(undefined);
  public readonly users$ = this._users.asObservable();

  loadUser(userID: number) {
    this.resetUser();
    this.userService
      .getUser(userID)
      .subscribe((user: User) => this._user.next(user));
  }

  loadUsers() {
    this.resetUsers();
    this.userService.getUsers().subscribe((users) => this._users.next(users));
  }

  resetUser() {
    this._user.next(undefined);
  }

  resetUsers() {
    this._users.next(undefined);
  }
}
