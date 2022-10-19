/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { User } from 'src/app/schemes';
import { ProjectUserService } from 'src/app/services/repository-user/repository-user.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css'],
})
export class UserSettingsComponent implements OnInit {
  createUserFormGroup = new FormGroup({
    username: new FormControl('', [
      Validators.required,
      this.userAlreadyExistsValidator(),
    ]),
  });

  users: User[] = [];
  search = '';

  constructor(
    public userService: UserService,
    public repoUserService: ProjectUserService,
    private navbarService: NavBarService,
    private toastService: ToastService
  ) {
    this.navbarService.title = 'Settings / Core / Users';
  }

  ngOnInit(): void {
    this.getUsers();
  }

  get username(): FormControl {
    return this.createUserFormGroup.get('username') as FormControl;
  }

  userAlreadyExistsValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (this.users) {
        for (const user of this.users) {
          if (user.name == control.value) {
            return { userAlreadyExists: true };
          }
        }
      }
      return null;
    };
  }

  createUser() {
    if (this.createUserFormGroup.valid) {
      const username = this.createUserFormGroup.value.username!;

      this.userService.createUser(username, 'user').subscribe({
        next: () => {
          this.toastService.showSuccess(
            'User created',
            `The user ${username} has been created.`
          );
          this.getUsers();
        },
      });
    }
  }

  createAdministratorWithUsername(username: string) {
    this.userService.updateRoleOfUser(username, 'administrator').subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Role of user updated',
          username + ' has now the role administrator'
        );
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'Update of role failed',
          'The role of ' + username + ' has not been updated'
        );
      },
    });
  }

  getUsers() {
    this.userService.getUsers().subscribe((res: User[]) => {
      this.users = res;
    });
  }

  removeAdministrator(username: string) {
    this.userService.updateRoleOfUser(username, 'user').subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Role of user updated',
          username + ' has now the role user'
        );
        this.getUsers();
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'Update of role failed',
          'The role of ' + username + ' has not been updated'
        );
      },
    });
  }

  deleteUser(username: string) {
    this.userService.deleteUser(username).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'User deleted',
          username + ' has been deleted'
        );
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'User deletion failed',
          username + ' has not been deleted'
        );
      },
    });
  }

  getUsersByRole(role: 'administrator' | 'user'): User[] {
    return this.users.filter(
      (u) =>
        u.role == role &&
        u.name.toLowerCase().includes(this.search.toLowerCase())
    );
  }
}
