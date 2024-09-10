/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { KeyValuePipe } from '@angular/common';
import { Component, Inject } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatRadioModule } from '@angular/material/radio';
import { MatSelect } from '@angular/material/select';
import { Observable, map, take } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Project, ProjectUserPermission } from 'src/app/openapi';
import {
  ProjectUserService,
  SimpleProjectUserRole,
} from 'src/app/projects/project-detail/project-users/service/project-user.service';

@Component({
  selector: 'app-add-user-to-project',
  templateUrl: './add-user-to-project.component.html',
  styleUrls: ['./add-user-to-project.component.css'],
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatRadioModule,
    MatError,
    MatSelect,
    MatOption,
    MatButton,
    MatIcon,
    KeyValuePipe,
  ],
})
export class AddUserToProjectDialogComponent {
  addUserToProjectForm = new FormGroup(
    {
      username: new FormControl('', {
        validators: [Validators.required],
        asyncValidators: [this.asyncUserAlreadyInProjectValidator()],
      }),
      role: new FormControl('user', Validators.required),
      permission: new FormControl('read'),
      reason: new FormControl('', Validators.required),
    },
    this.permissionRequiredValidator(),
  );

  constructor(
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
    private matDialogRef: MatDialogRef<AddUserToProjectDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { project: Project },
  ) {}

  get permissions() {
    return ProjectUserService.PERMISSIONS;
  }

  get roles() {
    return ProjectUserService.ROLES;
  }

  asyncUserAlreadyInProjectValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.projectUserService.projectUsers$.pipe(
        take(1),
        map((projectUsers) => {
          if (
            projectUsers?.find((pUser) => pUser.user.name === control.value)
          ) {
            return { userAlreadyInProjectError: true };
          }
          return null;
        }),
      );
    };
  }

  get username(): FormControl {
    return this.addUserToProjectForm.get('username') as FormControl;
  }

  permissionRequiredValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const permission = control.get('permission')!;
      const role = control.get('role');
      if (
        permission?.value in ProjectUserService.PERMISSIONS ||
        role?.value == 'manager'
      ) {
        permission?.setErrors(null);
        return null;
      }
      permission?.setErrors({ permissionInvalid: true });
      return { permissionInvalid: true };
    };
  }

  addUser(): void {
    if (this.addUserToProjectForm.valid) {
      const formValue = this.addUserToProjectForm.value;

      const permission =
        formValue.role === 'manager' ? 'write' : formValue.permission;
      this.projectUserService
        .addUserToProject(
          this.data.project.slug,
          formValue.username as string,
          formValue.role as SimpleProjectUserRole,
          permission as ProjectUserPermission,
          formValue.reason as string,
        )
        .subscribe(() => {
          this.addUserToProjectForm.reset();
          this.toastService.showSuccess(
            `User added`,
            `User '${formValue.username}' has been added to project '${this.data.project.name}'`,
          );
          this.close();
        });
    }
  }

  close(): void {
    this.matDialogRef.close();
  }
}
