/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import { User } from 'src/app/openapi';
import {
  UserRole,
  OwnUserWrapperService,
} from 'src/app/services/user/user.service';

export const mockUser: Readonly<User> = {
  id: 1,
  name: 'fakeUser',
  idp_identifier: 'identifier',
  email: 'test@example.com',
  role: 'user',
  created: '2024-04-29T14:00:00Z',
  last_login: '2024-04-29T14:59:00Z',
  beta_tester: false,
};

export class MockOwnUserWrapperService
  implements Partial<OwnUserWrapperService>
{
  _user = new BehaviorSubject<User | undefined>(undefined);
  user$ = this._user.asObservable();
  user: User | undefined = mockUser;

  constructor(user: User) {
    this._user.next(user);
    this.user = user;
  }

  validateUserRole(requiredRole: UserRole): boolean {
    const roles = ['user', 'administrator'];
    return roles.indexOf(requiredRole) <= roles.indexOf(this.user!.role);
  }
}

export class MockUserWrapperService implements Partial<OwnUserWrapperService> {
  _user = new BehaviorSubject<User | undefined>(undefined);
  user$ = this._user.asObservable();

  _users = new BehaviorSubject<User[] | undefined>(undefined);
  users$ = this._users.asObservable();

  constructor(
    user: User | undefined = undefined,
    users: User[] | undefined = undefined,
  ) {
    this._user.next(user);
    this._users.next(users);
  }

  loadUsers() {} // eslint-disable-line @typescript-eslint/no-empty-function
}
