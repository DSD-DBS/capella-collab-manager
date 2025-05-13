/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Tag, TagScope, User, UsersService } from 'src/app/openapi';

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

export function getUserTags(user: User): Tag[] {
  const tags = structuredClone(user.tags) || [];
  if (user.blocked) {
    tags.push({
      id: -1,
      name: 'Blocked',
      description:
        'The user is blocked and all authenticated requests are rejected.',
      hex_color: '#c10007',
      icon: 'no_accounts',
      scope: TagScope.User,
    });
  }
  if (user.beta_tester) {
    tags.push({
      id: -2,
      name: 'Beta Tester',
      description:
        'The user is signed up as beta user and helps to test experimental features.',
      hex_color: '#A020F0',
      icon: 'experiment',
      scope: TagScope.User,
    });
  }

  return tags;
}
