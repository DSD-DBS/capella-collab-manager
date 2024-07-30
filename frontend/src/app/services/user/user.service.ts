/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { UsersService, User } from 'src/app/openapi';
import { AuthenticationWrapperService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root',
})
export class UserWrapperService {
  _user = new BehaviorSubject<User | undefined>(undefined);
  user$ = this._user.asObservable();

  get user(): User | undefined {
    return this._user.value;
  }

  constructor(
    private authService: AuthenticationWrapperService,
    private usersService: UsersService,
  ) {
    this.updateOwnUser();
  }

  updateOwnUser(): void {
    if (this.authService.isLoggedIn()) {
      this.usersService.getCurrentUser().subscribe((res) => {
        this._user.next(res);
      });
    }
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

export type UserRole = 'user' | 'administrator';
