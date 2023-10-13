/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AfterViewInit, Component, OnInit, ViewChild } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatLegacyPaginator as MatPaginator } from '@angular/material/legacy-paginator';
import { MatLegacyTableDataSource as MatTableDataSource } from '@angular/material/legacy-table';
import { HistoryEvent } from 'src/app/events/service/events.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import {
  User,
  UserHistory,
  UserRole,
  UserService,
} from 'src/app/services/user/user.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css'],
})
export class UserSettingsComponent implements OnInit, AfterViewInit {
  @ViewChild(MatPaginator) paginator: MatPaginator | null = null;
  displayedColumns: string[] = [
    'eventType',
    'executorName',
    'executionTime',
    'projectName',
    'reason',
  ];

  users: User[] = [];
  search = '';
  selectedUser?: User;
  selectedUserHistory?: UserHistory;

  historyEventDataSource = new MatTableDataSource<HistoryEvent>([]);

  createUserFormGroup = new FormGroup({
    username: new FormControl('', [
      Validators.required,
      this.userAlreadyExistsValidator(),
    ]),
  });

  constructor(
    public userService: UserService,
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.getUsers();
  }

  ngAfterViewInit(): void {
    this.historyEventDataSource.paginator = this.paginator;
  }

  get username(): FormControl {
    return this.createUserFormGroup.get('username') as FormControl;
  }

  userAlreadyExistsValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (this.users.find((user) => user.name == control.value)) {
        return { userAlreadyExists: true };
      }
      return null;
    };
  }

  createUser() {
    const reason = this.getReason();
    if (!reason) {
      return;
    }

    if (this.createUserFormGroup.valid) {
      const username = this.createUserFormGroup.value.username!;

      this.userService.createUser(username, 'user', reason).subscribe({
        next: () => {
          this.toastService.showSuccess(
            'User created',
            `The user ${username} has been created.`,
          );
          this.getUsers();
        },
      });
    }
  }

  upgradeToAdministrator(user: User) {
    const reason = this.getReason();
    if (!reason) {
      return;
    }

    this.userService.updateRoleOfUser(user, 'administrator', reason).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Role of user updated',
          user.name + ' has now the role administrator',
        );
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'Update of role failed',
          'The role of ' + user.name + ' has not been updated',
        );
      },
    });
  }

  downgradeToUser(user: User) {
    const reason = this.getReason();
    if (!reason) {
      return;
    }

    this.userService.updateRoleOfUser(user, 'user', reason).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Role of user updated',
          user.name + ' has now the role user',
        );
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'Update of role failed',
          'The role of ' + user.name + ' has not been updated',
        );
      },
    });
  }

  deleteUser(user: User) {
    this.userService.deleteUser(user).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'User deleted',
          user.name + ' has been deleted',
        );
        this.getUsers();
      },
      error: () => {
        this.toastService.showError(
          'User deletion failed',
          user.name + ' has not been deleted',
        );
      },
    });
  }

  getUsers() {
    this.userService.getUsers().subscribe((users: User[]) => {
      this.selectedUser = undefined;
      this.selectedUserHistory = undefined;
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

  onUserSelect(user: User) {
    this.selectedUser = user;
    this.selectedUserHistory = undefined;

    this.userService.getUserHistory(user).subscribe({
      next: (userHistory) => {
        this.selectedUserHistory = userHistory;
        this.historyEventDataSource.data = userHistory.events;
        this.historyEventDataSource.paginator = this.paginator;
      },
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
}
