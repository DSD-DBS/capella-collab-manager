/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import { User } from 'src/app/schemes';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import { UserService } from 'src/app/services/user/user.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css'],
})
export class UserSettingsComponent implements OnInit {
  createAdministratorFormGroup = new FormGroup({
    username: new FormControl('', [Validators.required]),
  });

  users: User[] = [];
  search = '';

  constructor(
    public userService: UserService,
    public repoUserService: RepositoryUserService,
    private navbarService: NavBarService,
    private toastService: ToastService
  ) {
    this.navbarService.title = 'Settings / Core / Users';
  }

  ngOnInit(): void {
    this.getUsers();
  }

  get username(): FormControl {
    return this.createAdministratorFormGroup.get('username') as FormControl;
  }

  createAdministrator() {
    if (this.createAdministratorFormGroup.valid) {
      this.userService
        .updateRoleOfUser(
          this.createAdministratorFormGroup.value.username as string,
          'administrator'
        )
        .subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Role of user updated',
              this.createAdministratorFormGroup.value.username +
                ' has now the role administrator'
            );
            this.getUsers();
          },
          error: () => {
            this.toastService.showError(
              'Update of role failed',
              'The role of ' +
                this.createAdministratorFormGroup.value.username +
                ' was not updated'
            );
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
