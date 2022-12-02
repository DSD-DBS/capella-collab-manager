/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  Input,
  OnChanges,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  FormGroupDirective,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ProjectUser,
  ProjectUserPermission,
  ProjectUserService,
  SimpleProjectUserRole,
} from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { Project } from 'src/app/services/project/project.service';
import { User, UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-project-user-settings',
  templateUrl: './project-user-settings.component.html',
  styleUrls: ['./project-user-settings.component.css'],
})
export class ProjectUserSettingsComponent implements OnChanges {
  @Input() project!: Project;

  projectUsers: ProjectUser[] = [];
  search = '';

  @ViewChild('users') users: any;

  addUserToProjectForm = new FormGroup(
    {
      username: new FormControl('', [
        Validators.required,
        this.userAlreadyInProjectValidator(),
      ]),
      role: new FormControl('', Validators.required),
      permission: new FormControl(''),
    },
    this.permissionRequiredValidator()
  );

  constructor(
    public projectUserService: ProjectUserService,
    public userService: UserService,
    private toastService: ToastService
  ) {}

  ngOnChanges(_changes: SimpleChanges): void {
    this.refreshProjectUsers();
  }

  get username(): FormControl {
    return this.addUserToProjectForm.get('username') as FormControl;
  }

  get selectedUser(): ProjectUser {
    return this.users.selectedOptions.selected[0].value;
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
      return {};
    };
  }

  userAlreadyInProjectValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (this.projectUsers.find((pUser) => pUser.user.name == control.value)) {
        return { userAlreadyInProjectError: true };
      }
      return null;
    };
  }

  refreshProjectUsers(): void {
    this.projectUserService
      .getProjectUsers(this.project.slug)
      .subscribe((projectUsers) => {
        this.projectUsers = projectUsers;
      });
  }

  addUser(formDirective: FormGroupDirective): void {
    if (this.addUserToProjectForm.valid) {
      const formValue = this.addUserToProjectForm.value;

      let permission = formValue.permission;
      if (formValue.role == 'manager') {
        permission = 'write';
      }
      this.projectUserService
        .addUserToProject(
          this.project.slug,
          formValue.username as string,
          formValue.role as SimpleProjectUserRole,
          permission as string
        )
        .subscribe(() => {
          formDirective.resetForm();
          this.addUserToProjectForm.reset();
          this.refreshProjectUsers();
          this.toastService.showSuccess(
            `User added`,
            `User '${formValue.username}' has been added to project '${this.project.name}'`
          );
        });
    }
  }

  removeUserFromProject(user: User): void {
    this.projectUserService
      .deleteUserFromProject(this.project.slug, user.id)
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User removed`,
          `User '${user.name}' has been removed from project '${this.project.name}'`
        );
      });
  }

  upgradeUserToProjectManager(user: User): void {
    this.projectUserService
      .changeRoleOfProjectUser(this.project.slug, user.id, 'manager')
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' can now manage the project '${this.project.name}'`
        );
      });
  }

  downgradeUserToUserRole(user: User): void {
    this.projectUserService
      .changeRoleOfProjectUser(this.project.slug, user.id, 'user')
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' is no longer project lead in the project '${this.project.name}'`
        );
      });
  }

  setUserPermission(user: User, permission: ProjectUserPermission): void {
    this.projectUserService
      .changePermissionOfProjectUser(this.project.slug, user.id, permission)
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' has the permission '${permission}' in the project '${this.project.name}' now`
        );
      });
  }

  getProjectUsersByRole(role: SimpleProjectUserRole): ProjectUser[] {
    return this.projectUsers.filter(
      (pUser) =>
        pUser.role == role &&
        pUser.user.name.toLowerCase().includes(this.search.toLowerCase())
    );
  }
}
