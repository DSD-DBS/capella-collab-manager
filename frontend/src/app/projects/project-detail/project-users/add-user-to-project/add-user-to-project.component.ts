/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Observable, map, take } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ProjectUserService,
  SimpleProjectUserRole,
} from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { Project } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-add-user-to-project',
  templateUrl: './add-user-to-project.component.html',
  styleUrls: ['./add-user-to-project.component.css'],
})
export class AddUserToProjectDialogComponent {
  addUserToProjectForm = new FormGroup(
    {
      username: new FormControl('', {
        validators: [Validators.required],
        asyncValidators: [this.asyncUserAlreadyInProjectValidator()],
      }),
      role: new FormControl('', Validators.required),
      permission: new FormControl(''),
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
        permission?.value in this.projectUserService.PERMISSIONS ||
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
          permission as string,
          formValue.reason as string,
        )
        .subscribe(() => {
          this.addUserToProjectForm.reset();
          this.toastService.showSuccess(
            `User added`,
            `User '${formValue.username}' has been added to project '${this.data.project.name}'`,
          );
          this.matDialogRef.close();
        });
    }
  }
}
