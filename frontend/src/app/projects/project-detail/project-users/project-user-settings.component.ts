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
import { ProjectUser } from 'src/app/schemes';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import { UserService } from 'src/app/services/user/user.service';
import { ToastService } from 'src/app/toast/toast.service';
import { Project } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-user-settings',
  templateUrl: './project-user-settings.component.html',
  styleUrls: ['./project-user-settings.component.css'],
})
export class RepositoryUserSettingsComponent implements OnChanges {
  @Input() repository!: Project;

  repositoryUsers: Array<ProjectUser> = [];
  search = '';

  @ViewChild('users') users: any;

  addUserToRepoForm = new FormGroup(
    {
      username: new FormControl('', [
        Validators.required,
        this.userAlreadyInRepositoryValidator(),
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

  userAlreadyInRepositoryValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      for (let repoUser of this.repositoryUsers) {
        if (repoUser.username == control.value) {
          return { userAlreadyInRepositoryError: true };
        }
      }
      return null;
    };
  }

  refreshRepoUsers(): void {
    this.repoUserService.getRepoUsers(this.repository.name).subscribe((res) => {
      this.repositoryUsers = res;
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
          this.repository.name,
          formValue.username as string,
          formValue.role as 'user' | 'manager',
          permission as string
        )
        .subscribe(() => {
          formDirective.resetForm();
          this.addUserToRepoForm.reset();
          this.refreshRepoUsers();
          this.toastService.showSuccess(
            'User added to project ' + this.repository.name,
            ''
          );
        });
    }
  }

  removeUserFromRepo(username: string): void {
    this.repoUserService
      .deleteUserFromRepo(this.repository.name, username)
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  upgradeUserToRepositoryManager(username: string): void {
    this.repoUserService
      .changeRoleOfRepoUser(this.repository.name, username, 'manager')
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  downgradeUserToUserRole(username: string): void {
    this.repoUserService
      .changeRoleOfRepoUser(this.repository.name, username, 'user')
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  setUserPermission(username: string, permission: 'read' | 'write'): void {
    this.repoUserService
      .changePermissionOfRepoUser(this.repository.name, username, permission)
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  getRepositoryUsersByRole(role: 'manager' | 'user'): Array<ProjectUser> {
    return this.repositoryUsers.filter(
      (u) => u.role == role && u.username.includes(this.search.toLowerCase())
    );
  }
}
