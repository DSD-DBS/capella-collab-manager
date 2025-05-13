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
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';
import { mockUserTag } from 'src/storybook/tags';

export const mockUser: Readonly<User> = {
  id: 1,
  name: 'User XYZ',
  idp_identifier: 'identifier',
  email: 'test@example.com',
  role: 'user',
  created: '2024-04-29T14:00:00Z',
  last_login: '2024-04-29T14:59:00Z',
  beta_tester: false,
  blocked: false,
  tags: [mockUserTag],
};

class MockOwnUserWrapperService implements Partial<OwnUserWrapperService> {
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

export const mockOwnUserWrapperServiceProvider = (user: User) => {
  return {
    provide: OwnUserWrapperService,
    useValue: new MockOwnUserWrapperService(user),
  };
};

class MockUserWrapperService implements Partial<UserWrapperService> {
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

export const mockUserWrapperServiceProvider = (
  user: User | undefined = undefined,
  users: User[] | undefined = undefined,
) => {
  return {
    provide: UserWrapperService,
    useValue: new MockUserWrapperService(user, users),
  };
};
