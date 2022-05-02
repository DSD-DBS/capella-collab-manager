// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, EventEmitter, Input, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatSelectChange } from '@angular/material/select';
import { Session } from 'src/app/schemes';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import {
  Repository,
  Warnings,
} from 'src/app/services/repository/repository.service';
import { SessionService } from 'src/app/services/session/session.service';

@Component({
  selector: 'app-request-session',
  templateUrl: './request-session.component.html',
  styleUrls: ['./request-session.component.css'],
})
export class RequestSessionComponent implements OnInit {
  showSpinner = false;
  creationSuccessful = false;
  repositoryFormGroup = new FormGroup(
    {
      workspaceSwitch: new FormControl(true),
      repository: new FormControl(''),
    },
    this.validateForm()
  );

  get repository(): FormControl {
    return this.repositoryFormGroup.get('repository') as FormControl;
  }

  get workspaceSwitch(): FormControl {
    return this.repositoryFormGroup.get('workspaceSwitch') as FormControl;
  }

  @Input()
  repositories: Array<Repository> = [];

  warnings: Array<Warnings> = [];

  permissions: any = {};

  session: Session | undefined = undefined;
  connectionTypeHelpIsOpen = false;
  persistentWorkspaceHelpIsOpen = false;
  cleanWorkspaceHelpIsOpen = false;

  constructor(
    public sessionService: SessionService,
    private repoUserService: RepositoryUserService
  ) {}

  ngOnInit(): void {}

  validateForm(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (
        control.get('workspaceSwitch')?.value &&
        !control.get('repository')?.value
      ) {
        control.get('repository')?.setErrors({ repositoryRequired: true });
        return { repositoryRequired: true };
      }
      control.get('repository')?.setErrors(null);
      return null;
    };
  }

  requestSession() {
    if (this.repositoryFormGroup.valid) {
      this.showSpinner = true;
      this.creationSuccessful = false;
      let type: 'readonly' | 'persistent' = 'readonly';
      if (this.workspaceSwitch.value) {
        type = 'readonly';
      } else {
        type = 'persistent';
      }
      this.sessionService
        .createNewSession(type, this.repository.value)
        .subscribe(
          (res) => {
            this.session = res;
            this.showSpinner = false;
            this.creationSuccessful = true;
          },
          () => {
            this.showSpinner = false;
          }
        );
    }
  }

  setPermissionsAndWarningsByName(event: MatSelectChange): void {
    this.permissions = {};
    this.warnings = [];
    for (let repo of this.repositories) {
      if (repo.repository_name == event.value) {
        for (let permission of repo.permissions) {
          this.permissions[permission] =
            this.repoUserService.PERMISSIONS[permission];
        }
        this.warnings = repo.warnings;
        return;
      }
    }
    this.permissions = {};
  }
}
