/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatIconButton, MatButton } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import {
  MatFormField,
  MatLabel,
  MatSuffix,
  MatError,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatListSubheaderCssMatStyler } from '@angular/material/list';
import { MatTooltip } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import {
  InputDialogComponent,
  InputDialogResult,
} from 'src/app/helpers/input-dialog/input-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Role, User, UsersService } from 'src/app/openapi';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import {
  UserRole,
  UserWrapperService,
} from 'src/app/services/user/user.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  standalone: true,
  imports: [
    MatFormField,
    MatLabel,
    MatInput,
    FormsModule,
    MatIcon,
    MatSuffix,
    MatListSubheaderCssMatStyler,
    RouterLink,
    MatIconButton,
    MatTooltip,
    ReactiveFormsModule,
    MatError,
    MatButton,
  ],
})
export class UserSettingsComponent implements OnInit {
  users: User[] = [];
  search = '';
  selectedUser?: User;

  createUserFormGroup = new FormGroup({
    username: new FormControl('', [
      Validators.required,
      this.userNameAlreadyExistsValidator(),
    ]),
    idpIdentifier: new FormControl('', [
      Validators.required,
      this.userIdPIdentifierAlreadyExistsValidator(),
    ]),
  });

  constructor(
    public userService: UserWrapperService,
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
    private dialog: MatDialog,
    private usersService: UsersService,
  ) {}

  ngOnInit(): void {
    this.getUsers();
  }

  get username(): FormControl {
    return this.createUserFormGroup.controls.username;
  }

  get idpIdentifier(): FormControl {
    return this.createUserFormGroup.controls.idpIdentifier;
  }

  get advanced_roles() {
    return ProjectUserService.ADVANCED_ROLES;
  }

  userNameAlreadyExistsValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (this.users.find((user) => user.name == control.value)) {
        return { userAlreadyExists: true };
      }
      return null;
    };
  }

  userIdPIdentifierAlreadyExistsValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (this.users.find((user) => user.idp_identifier == control.value)) {
        return { userAlreadyExists: true };
      }
      return null;
    };
  }

  createUser() {
    const username = this.createUserFormGroup.value.username;
    const idpIdentifier = this.createUserFormGroup.value.idpIdentifier;

    if (this.createUserFormGroup.invalid || !username || !idpIdentifier) {
      return;
    }

    const dialogRef = this.dialog.open(InputDialogComponent, {
      data: {
        title: 'Create User',
        text: `Please provide a reason why you want to create the user '${username}.' manually.`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.usersService
          .createUser({
            name: username,
            idp_identifier: idpIdentifier,
            role: Role.User,
            reason: result.text,
          })
          .subscribe({
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
        text: `Please provide a reason to upgrade the user '${user.name}' to the role administrator.`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.usersService
          .updateUser(user.id, {
            role: Role.Administrator,
            reason: result.text,
          })
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
        text: `Please provide a reason to downgrade the user '${user.name}' to the role user.`,
      },
    });

    dialogRef.afterClosed().subscribe((result: InputDialogResult) => {
      if (result.success && result.text) {
        this.usersService
          .updateUser(user.id, { role: Role.User, reason: result.text })
          .subscribe({
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
        text:
          `Do you really want to delete the user ${user.name}?<br>` +
          '- The user will be removed from all projects<br>' +
          '- All events related to the user will be deleted<br>' +
          '- All workspaces of the user will be deleted (including all data)<br>' +
          '<b>The action is irrevocable.</b>',
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.usersService.deleteUser(user.id).subscribe({
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
    this.usersService.getUsers().subscribe((users: User[]) => {
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
}
