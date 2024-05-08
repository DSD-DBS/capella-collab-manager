/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  User,
  UserRole,
  UserService,
} from 'src/app/services/user/user.service';

export const mockUser: Readonly<User> = {
  id: 1,
  name: 'fakeUser',
  role: 'user',
  created: '2024-04-29T14:00:00Z',
  last_login: '2024-04-29T14:59:00Z',
};

export class MockUserService implements Partial<UserService> {
  role: UserRole;

  constructor(role: UserRole) {
    this.role = role;
  }

  validateUserRole(requiredRole: UserRole): boolean {
    const roles = ['user', 'administrator'];
    return roles.indexOf(requiredRole) <= roles.indexOf(this.role);
  }
}
