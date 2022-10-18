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
import { ProjectUser, User } from 'src/app/schemes';
import { Project } from 'src/app/services/project/project.service';
import { ProjectUserService } from 'src/app/services/repository-user/repository-user.service';
import { UserService } from 'src/app/services/user/user.service';

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

  addUserToRepoForm = new FormGroup(
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
    this.refreshRepoUsers();
  }

  get username(): FormControl {
    return this.addUserToRepoForm.get('username') as FormControl;
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
      for (const projectUser of this.projectUsers) {
        if (projectUser.user.name == control.value) {
          return { userAlreadyInProjectError: true };
        }
      }
      return null;
    };
  }

  refreshRepoUsers(): void {
    this.projectUserService.getRepoUsers(this.project.name).subscribe((res) => {
      this.projectUsers = res;
    });
  }

  addUser(formDirective: FormGroupDirective): void {
    if (this.addUserToRepoForm.valid) {
      const formValue = this.addUserToRepoForm.value;

      let permission = formValue.permission;
      if (formValue.role == 'manager') {
        permission = 'write';
      }
      this.projectUserService
        .addUserToRepo(
          this.project.name,
          formValue.username as string,
          formValue.role as 'user' | 'manager',
          permission as string
        )
        .subscribe(() => {
          formDirective.resetForm();
          this.addUserToRepoForm.reset();
          this.refreshRepoUsers();
          this.toastService.showSuccess(
            `User added`,
            `User '${formValue.username}' has been added to project '${this.project.name}'`
          );
        });
    }
  }

  removeUserFromRepo(user: User): void {
    this.projectUserService
      .deleteUserFromRepo(this.project.name, user.id)
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User removed`,
          `User '${user.name}' has been removed from project '${this.project.name}'`
        );
      });
  }

  upgradeUserToProjectManager(user: User): void {
    this.projectUserService
      .changeRoleOfRepoUser(this.project.name, user.id, 'manager')
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' can now manage the project '${this.project.name}'`
        );
      });
  }

  downgradeUserToUserRole(user: User): void {
    this.projectUserService
      .changeRoleOfRepoUser(this.project.name, user.id, 'user')
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' is no longer project lead in the project '${this.project.name}'`
        );
      });
  }

  setUserPermission(user: User, permission: 'read' | 'write'): void {
    this.projectUserService
      .changePermissionOfRepoUser(this.project.name, user.id, permission)
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' has the permission '${permission}' in the project '${this.project.name}' now`
        );
      });
  }

  getProjectUsersByRole(role: 'manager' | 'user'): ProjectUser[] {
    return this.projectUsers.filter(
      (u) => u.role == role && u.user.name.includes(this.search.toLowerCase())
    );
  }
}
