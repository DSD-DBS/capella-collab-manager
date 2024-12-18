/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  Validators,
  FormsModule,
  ReactiveFormsModule,
  AsyncValidatorFn,
} from '@angular/forms';
import { MatIconButton, MatButton } from '@angular/material/button';
import { MatChipListbox, MatChipOption } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import {
  MatFormField,
  MatLabel,
  MatSuffix,
  MatError,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatTooltip } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { map, Observable, take } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import {
  InputDialogComponent,
  InputDialogResult,
} from 'src/app/helpers/input-dialog/input-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Role, User, UsersService } from 'src/app/openapi';
import {
  UserRole,
  OwnUserWrapperService,
} from 'src/app/services/user/user.service';
import { UserWrapperService } from 'src/app/users/user-wrapper/user-wrapper.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  imports: [
    MatFormField,
    MatLabel,
    MatInput,
    FormsModule,
    MatIcon,
    MatSuffix,
    RouterLink,
    MatIconButton,
    MatTooltip,
    ReactiveFormsModule,
    MatError,
    MatButton,
    AsyncPipe,
    NgxSkeletonLoaderModule,
    MatChipListbox,
    MatChipOption,
  ],
})
export class UserSettingsComponent implements OnInit {
  public readonly roleMapping = {
    user: 'Global User',
    administrator: 'Global Administrator',
  };

  createUserFormGroup = new FormGroup({
    username: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.asyncUserNameAlreadyExistsValidator(),
    }),
    idpIdentifier: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.asyncUserIdPIdentifierAlreadyExistsValidator(),
    }),
  });

  form = new FormGroup({
    search: new FormControl<string>(''),
    userType: new FormControl<string | null>(null),
  });

  constructor(
    public ownUserService: OwnUserWrapperService,
    public userWrapperService: UserWrapperService,
    private toastService: ToastService,
    private dialog: MatDialog,
    private usersService: UsersService,
  ) {}

  ngOnInit(): void {
    this.userWrapperService.loadUsers();
  }

  get username(): FormControl {
    return this.createUserFormGroup.controls.username;
  }

  get idpIdentifier(): FormControl {
    return this.createUserFormGroup.controls.idpIdentifier;
  }

  get userRoles() {
    return Object.values(Role);
  }

  asyncUserNameAlreadyExistsValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.userWrapperService.users$.pipe(
        take(1),
        map((users) => {
          return users?.find((user) => user.name == control.value)
            ? { userAlreadyExists: true }
            : null;
        }),
      );
    };
  }

  asyncUserIdPIdentifierAlreadyExistsValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.userWrapperService.users$.pipe(
        take(1),
        map((users) => {
          return users?.find((user) => user.idp_identifier == control.value)
            ? { userAlreadyExists: true }
            : null;
        }),
      );
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
              this.userWrapperService.loadUsers();
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
              this.userWrapperService.loadUsers();
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
              this.userWrapperService.loadUsers();
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
            this.userWrapperService.loadUsers();
          },
        });
      }
    });
  }

  getUsersByRole(
    users: User[] | null | undefined,
    role: UserRole,
  ): User[] | undefined {
    return users?.filter((user) => {
      const roleMatches = user.role == role;
      const searchMatches = user.name
        .toLowerCase()
        .includes(this.form.value.search?.toLowerCase() || '');
      const userTypeMatches =
        this.form.value.userType == null ||
        user.beta_tester == (this.form.value.userType == 'beta');
      return roleMatches && searchMatches && userTypeMatches;
    });
  }
}
