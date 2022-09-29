/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import { Project } from 'src/app/services/project/project.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-set-t4c-password',
  templateUrl: './set-t4c-password.component.html',
  styleUrls: ['./set-t4c-password.component.css'],
})
export class SetT4CPasswordComponent implements OnInit {
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
      if (value.repository && value.password) {
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
}
