/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { FormGroupDirective } from '@angular/forms';
import {
  AbstractControl,
  AsyncValidatorFn,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import { Observable, filter, map, take } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ProjectUserService,
  SimpleProjectUserRole,
} from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-add-user-to-project',
  templateUrl: './add-user-to-project.component.html',
  styleUrls: ['./add-user-to-project.component.css'],
})
export class AddUserToProjectComponent {
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
    this.permissionRequiredValidator()
  );

  constructor(
    public projectUserService: ProjectUserService,
    private projectService: ProjectService,
    private toastService: ToastService,
    private matDialogRef: MatDialogRef<AddUserToProjectComponent>
  ) {}

  asyncUserAlreadyInProjectValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.projectUserService.projectUsers.pipe(
        take(1),
        map((projectUsers) => {
          if (
            projectUsers?.find((pUser) => pUser.user.name === control.value)
          ) {
            return { userAlreadyInProjectError: true };
          }
          return null;
        })
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

  addUser(formDirective: FormGroupDirective): void {
    this.projectService.project.pipe(filter(Boolean)).subscribe((project) => {
      if (this.addUserToProjectForm.valid) {
        const formValue = this.addUserToProjectForm.value;

        let permission = formValue.permission;
        if (formValue.role == 'manager') {
          permission = 'write';
        }
        this.projectUserService
          .addUserToProject(
            project.slug,
            formValue.username as string,
            formValue.role as SimpleProjectUserRole,
            permission as string,
            formValue.reason as string
          )
          .subscribe(() => {
            formDirective.resetForm();
            this.addUserToProjectForm.reset();
            this.projectUserService.loadProjectUsers();
            this.toastService.showSuccess(
              `User added`,
              `User '${formValue.username}' has been added to project '${project?.name}'`
            );
            this.matDialogRef.close();
          });
      }
    });
  }
}
