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
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import {
  InputDialogComponent,
  InputDialogResult,
} from 'src/app/helpers/input-dialog/input-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import {
  User,
  UserRole,
  UserService,
} from 'src/app/services/user/user.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css'],
})
export class UserSettingsComponent implements OnInit {
  users: User[] = [];
  search = '';
  selectedUser?: User;

  createUserFormGroup = new FormGroup({
    username: new FormControl('', [
      Validators.required,
      this.userAlreadyExistsValidator(),
    ]),
  });

  constructor(
    public userService: UserService,
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
    private dialog: MatDialog,
  ) {}

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
    if (!this.createUserFormGroup.valid) {
      return;
    }

    const username = this.createUserFormGroup.value.username!;

    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: 'Create User',
        text: `Do you really want to create the user '${username}? Please provide a reason.'`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.userService.createUser(username, 'user', result.text).subscribe({
          next: () => {
            this.toastService.showSuccess(
              'User created',
              `The user ${username} has been created.`,
            );
            this.getUsers();
          },
        });
      }
    });
  }

  upgradeToAdministrator(user: User) {
    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: 'Upgrade to Administrator Role',
        text: `Do you really want to upgrade ${user.name} to Administrator? Please provide a reason.'`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.userService
          .updateRoleOfUser(user, 'administrator', result.text)
          .subscribe({
            next: () => {
              this.toastService.showSuccess(
                'Role of user updated',
                user.name + ' has now the role administrator',
              );
              this.getUsers();
            },
          });
      }
    });
  }

  downgradeToUser(user: User) {
    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: 'Downgrade to User Role',
        text: `Do you really want to downgrade ${user.name} to User? Please provide a reason.'`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.userService.updateRoleOfUser(user, 'user', result.text).subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Role of user updated',
              user.name + ' has now the role user',
            );
            this.getUsers();
          },
        });
      }
    });
  }

  deleteUser(user: User) {
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Delete User',
        text: `Do you really want to delete the user ${user.name}?`,
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.userService.deleteUser(user).subscribe({
          next: () => {
            this.toastService.showSuccess(
              'User deleted',
              user.name + ' has been deleted',
            );
            this.getUsers();
          },
        });
      }
    });
  }

  getUsers() {
    this.userService.getUsers().subscribe((users: User[]) => {
      this.selectedUser = undefined;
      this.users = users;
    });
  }

  getUsersByRole(role: UserRole): User[] {
    return this.users.filter(
      (user) =>
        user.role == role &&
        user.name.toLowerCase().includes(this.search.toLowerCase()),
    );
  }

  onUserSelect(user: User) {
    this.selectedUser = user;
  }
}
