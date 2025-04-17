/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import {
  ProjectUser,
  ProjectUserPermission,
  ProjectUserRole,
} from 'src/app/openapi';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { mockUser } from './user';

export const mockProjectUsers: ProjectUser[] = [
  {
    role: 'administrator',
    permission: 'write',
    user: { ...mockUser, name: 'administrator1' },
  },
  {
    role: 'administrator',
    permission: 'write',
    user: { ...mockUser, name: 'administrator2' },
  },
  {
    role: 'user',
    permission: 'write',
    user: { ...mockUser, name: 'projectuser1' },
  },
  {
    role: 'user',
    permission: 'read',
    user: { ...mockUser, name: 'projectuserWithReallyLongName', blocked: true },
  },
  {
    role: 'manager',
    permission: 'write',
    user: { ...mockUser, name: 'projectadmin1' },
  },
];

class MockProjectUserService implements Partial<ProjectUserService> {
  role: ProjectUserRole;
  permission: ProjectUserPermission | undefined;

  private _projectUsers = new BehaviorSubject<ProjectUser[] | undefined>(
    undefined,
  );
  public readonly projectUsers$ = this._projectUsers.asObservable();

  constructor(
    role: ProjectUserRole,
    permission: ProjectUserPermission | undefined = undefined,
    projectUsers: ProjectUser[] | undefined = undefined,
  ) {
    this.role = role;
    this.permission = permission;
    this._projectUsers.next(projectUsers);
  }

  verifyRole(requiredRole: ProjectUserRole): boolean {
    const roles = ['user', 'manager', 'administrator'];
    return roles.indexOf(requiredRole) <= roles.indexOf(this.role);
  }

  verifyPermission(requiredPermission: string): boolean {
    if (this.permission === undefined) return false;
    const permissions = ['read', 'write'];
    return (
      permissions.indexOf(requiredPermission) <=
      permissions.indexOf(this.permission)
    );
  }
}

export const mockProjectUserServiceProvider = (
  role: ProjectUserRole,
  permission: ProjectUserPermission | undefined = undefined,
  projectUsers: ProjectUser[] | undefined = undefined,
) => {
  return {
    provide: ProjectUserService,
    useValue: new MockProjectUserService(role, permission, projectUsers),
  };
};
