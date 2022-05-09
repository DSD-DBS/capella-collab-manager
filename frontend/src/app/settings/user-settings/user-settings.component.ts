// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import {
  Project,
  ProjectService,
} from 'src/app/projects/service/project.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-user-settings',
  templateUrl: './user-settings.component.html',
  styleUrls: ['./user-settings.component.css'],
})
export class UserSettingsComponent implements OnInit {
  constructor(
    private repositoryUserService: RepositoryUserService,
    private userService: UserService
  ) {}
  repositories: Array<Project> = [];
  updatePasswordSuccess = false;

  updatePasswordForm = new FormGroup({
    repository: new FormControl('', Validators.required),
    password: new FormControl('', [
      Validators.required,
      Validators.minLength(8),
    ]),
  });

  get repository(): FormControl {
    return this.updatePasswordForm.get('repository') as FormControl;
  }

  get password(): FormControl {
    return this.updatePasswordForm.get('password') as FormControl;
  }

  ngOnInit(): void {
    // this.repositoryService.getProjects().subscribe((res: Array<Project>) => {
    //   this.repositories = res.filter((repo) => {
    //     return repo.permissions.includes('write');
    //   });
    // });
  }

  updatePassword(): void {
    if (this.updatePasswordForm.valid) {
      const value = this.updatePasswordForm.value;
      this.repositoryUserService
        .updatePasswordOfUser(
          value.repository,
          this.userService.getUsernameFromLocalStorage(),
          value.password
        )
        .subscribe(() => {
          this.updatePasswordSuccess = true;
          setTimeout(() => {
            this.updatePasswordSuccess = false;
          }, 3000);
        });
    }
  }
}
