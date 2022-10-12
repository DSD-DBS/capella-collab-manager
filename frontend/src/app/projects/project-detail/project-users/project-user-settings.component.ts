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
import { ProjectUser } from 'src/app/schemes';
import { Project } from 'src/app/services/project/project.service';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
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
    public repoUserService: RepositoryUserService,
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
      if (
        control.get('permission')?.value in this.repoUserService.PERMISSIONS ||
        control.get('role')?.value == 'manager'
      ) {
        control.get('permission')?.setErrors(null);
        return null;
      }
      control.get('permission')?.setErrors({ permissionInvalid: true });
      return {};
    };
  }

  userAlreadyInProjectValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      for (const repoUser of this.projectUsers) {
        if (repoUser.username == control.value) {
          return { userAlreadyInProjectError: true };
        }
      }
      return null;
    };
  }

  refreshRepoUsers(): void {
    this.repoUserService.getRepoUsers(this.project.name).subscribe((res) => {
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
      this.repoUserService
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

  removeUserFromRepo(username: string): void {
    this.repoUserService
      .deleteUserFromRepo(this.project.name, username)
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User removed`,
          `User '${username}' has been removed from project '${this.project.name}'`
        );
      });
  }

  upgradeUserToProjectManager(username: string): void {
    this.repoUserService
      .changeRoleOfRepoUser(this.project.name, username, 'manager')
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${username}' can now manage the project '${this.project.name}'`
        );
      });
  }

  downgradeUserToUserRole(username: string): void {
    this.repoUserService
      .changeRoleOfRepoUser(this.project.name, username, 'user')
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${username}' is no longer project lead in the project '${this.project.name}'`
        );
      });
  }

  setUserPermission(username: string, permission: 'read' | 'write'): void {
    this.repoUserService
      .changePermissionOfRepoUser(this.project.name, username, permission)
      .subscribe(() => {
        this.refreshRepoUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${username}' has the permission '${permission}' in the project '${this.project.name}' now`
        );
      });
  }

  getProjectUsersByRole(role: 'manager' | 'user'): ProjectUser[] {
    return this.projectUsers.filter(
      (u) => u.role == role && u.username.includes(this.search.toLowerCase())
    );
  }
}
