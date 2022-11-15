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
import { ProjectUserService } from 'src/app/services/project-user/project-user.service';
import { User, UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css'],
})
export class UserSettingsComponent implements OnInit {
  users: User[] = [];
  search = '';

  createUserFormGroup = new FormGroup({
    username: new FormControl('', [
      Validators.required,
      this.userAlreadyExistsValidator(),
    ]),
  });

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
      if (this.users.find((user) => user.name == control.value)) {
        return { userAlreadyExists: true };
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

  createAdministratorWithUsername(user: User) {
    this.userService.updateRoleOfUser(user, 'administrator').subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Role of user updated',
          user.name + ' has now the role administrator'
        );
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'Update of role failed',
          'The role of ' + user.name + ' has not been updated'
        );
      },
    });
  }

  getUsers() {
    this.userService.getUsers().subscribe((res: User[]) => {
      this.users = res;
    });
  }

  removeAdministrator(user: User) {
    this.userService.updateRoleOfUser(user, 'user').subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Role of user updated',
          user.name + ' has now the role user'
        );
        this.getUsers();
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'Update of role failed',
          'The role of ' + user.name + ' has not been updated'
        );
      },
    });
  }

  deleteUser(user: User) {
    this.userService.deleteUser(user).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'User deleted',
          user.name + ' has been deleted'
        );
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'User deletion failed',
          user.name + ' has not been deleted'
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
