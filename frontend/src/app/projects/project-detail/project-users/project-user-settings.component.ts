/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  OnChanges,
  OnInit,
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
import { MatLegacySelectionList as MatSelectionList } from '@angular/material/legacy-list';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ProjectUser,
  ProjectUserPermission,
  ProjectUserService,
  SimpleProjectUserRole,
} from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { User, UserService } from 'src/app/services/user/user.service';
import { Project, ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-user-settings',
  templateUrl: './project-user-settings.component.html',
  styleUrls: ['./project-user-settings.component.css'],
})
export class ProjectUserSettingsComponent implements OnInit, OnChanges {
  public project?: Project;

  projectUsers: ProjectUser[] = [];
  search = '';

  @ViewChild('users') users!: MatSelectionList;

  addUserToProjectForm = new FormGroup(
    {
      username: new FormControl('', [
        Validators.required,
        this.userAlreadyInProjectValidator(),
      ]),
      role: new FormControl('', Validators.required),
      permission: new FormControl(''),
      reason: new FormControl('', Validators.required),
    },
    this.permissionRequiredValidator()
  );

  constructor(
    public projectUserService: ProjectUserService,
    public userService: UserService,
    private toastService: ToastService,
    private projectService: ProjectService
  ) {}

  ngOnInit(): void {
    this.projectService.project
      .pipe(filter(Boolean), untilDestroyed(this))
      .subscribe((project) => (this.project = project));
  }

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
      .getProjectUsers(this.project?.slug!)
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
          this.project?.slug!,
          formValue.username as string,
          formValue.role as SimpleProjectUserRole,
          permission as string,
          formValue.reason as string
        )
        .subscribe(() => {
          formDirective.resetForm();
          this.addUserToProjectForm.reset();
          this.refreshProjectUsers();
          this.toastService.showSuccess(
            `User added`,
            `User '${formValue.username}' has been added to project '${this.project?.name}'`
          );
        });
    }
  }

  removeUserFromProject(user: User): void {
    const reason = this.getReason();
    if (!reason) {
      return;
    }

    this.projectUserService
      .deleteUserFromProject(this.project?.slug!, user.id, reason)
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User removed`,
          `User '${user.name}' has been removed from project '${this.project?.name}'`
        );
      });
  }

  upgradeUserToProjectManager(user: User): void {
    const reason = this.getReason();
    if (!reason) {
      return;
    }

    this.projectUserService
      .changeRoleOfProjectUser(this.project?.slug!, user.id, 'manager', reason)
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' can now manage the project '${this.project?.name}'`
        );
      });
  }

  downgradeUserToUserRole(user: User): void {
    const reason = this.getReason();
    if (!reason) {
      return;
    }

    this.projectUserService
      .changeRoleOfProjectUser(this.project?.slug!, user.id, 'user', reason)
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' is no longer project lead in the project '${this.project?.name}'`
        );
      });
  }

  setUserPermission(user: User, permission: ProjectUserPermission): void {
    const reason = this.getReason();
    if (!reason) {
      return;
    }

    this.projectUserService
      .changePermissionOfProjectUser(
        this.project?.slug!,
        user.id,
        permission,
        reason
      )
      .subscribe(() => {
        this.refreshProjectUsers();
        this.toastService.showSuccess(
          `User modified`,
          `User '${user.name}' has the permission '${permission}' in the project '${this.project?.name}' now`
        );
      });
  }

  getReason(): string | undefined {
    const reason = window.prompt('Please enter a reason!');
    if (!reason) {
      this.toastService.showError('Reason missing', 'You must enter a reason!');
      return;
    }
    return reason;
  }

  getProjectUsersByRole(role: SimpleProjectUserRole): ProjectUser[] {
    return this.projectUsers.filter(
      (pUser) =>
        pUser.role == role &&
        pUser.user.name.toLowerCase().includes(this.search.toLowerCase())
    );
  }
}
