// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import { MatSelectChange } from '@angular/material/select';
import { Session } from 'src/app/schemes';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import {
  Repository,
  Warnings,
} from 'src/app/services/repository/repository.service';
import {
  DepthType,
  SessionService,
} from 'src/app/services/session/session.service';

@Component({
  selector: 'app-request-session',
  templateUrl: './request-session.component.html',
  styleUrls: ['./request-session.component.css'],
})
export class RequestSessionComponent implements OnInit {
  showSpinner = false;
  creationSuccessful = false;

  history: Array<String> = ['Latest commit', 'Complete history'];
  isTag: boolean = false;

  repositoryFormGroup = new FormGroup(
    {
      workspaceSwitch: new FormControl(true),
      repository: new FormControl(''),
      reference: new FormControl('refs/heads/main'),
      historyDepth: new FormControl(this.history[0]),
    },
    this.validateForm()
  );

  get repository(): FormControl {
    return this.repositoryFormGroup.get('repository') as FormControl;
  }

  get reference(): FormControl {
    return this.repositoryFormGroup.get('reference') as FormControl;
  }

  get historyDepth(): FormControl {
    return this.repositoryFormGroup.get('historyDepth') as FormControl;
  }

  get workspaceSwitch(): FormControl {
    return this.repositoryFormGroup.get('workspaceSwitch') as FormControl;
  }

  @Input()
  repositories: Array<Repository> = [];

  chosenRepository: Repository | undefined = undefined;
  allBranches: boolean = false;

  warnings: Array<Warnings> = [];

  permissions: any = {};

  session: Session | undefined = undefined;
  connectionTypeHelpIsOpen = false;
  persistentWorkspaceHelpIsOpen = false;
  cleanWorkspaceHelpIsOpen = false;

  tags: Array<String> = [];
  branches: Array<String> = [];

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
      if (
        this.historyDepth.value == 'Latest commit' ||
        this.reference.value.startsWith('refs/tags/')
      ) {
        var depth = DepthType.LatestCommit;
      } else {
        var depth = DepthType.CompleteHistory;
      }
      var reference = this.reference.value;
      if (this.allBranches) {
        reference = 'All';
      }
      this.sessionService
        .createNewSession(type, this.repository.value, reference, depth)
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
        this.setBranches(repo);
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

  setBranches(repo: Repository) {
    this.chosenRepository = repo;
    this.tags = [];
    this.branches = [];
    for (var revision of repo.branches) {
      if (revision.endsWith('master')) {
        this.repositoryFormGroup.controls['reference'].setValue(
          'refs/heads/master'
        );
      } else if (revision.endsWith('main')) {
        this.repositoryFormGroup.controls['reference'].setValue(
          'refs/heads/main'
        );
      }
      if (revision.startsWith('refs/heads/')) {
        this.branches.push(revision);
      } else if (revision.startsWith('refs/tags/')) {
        this.tags.push(revision);
      }
    }
  }
  changeIsTag(event: MatSelectChange) {
    if (event.value.startsWith('refs/tags/')) {
      this.isTag = true;
    } else {
      this.isTag = false;
    }
  }

  changeAllBranches() {
    this.allBranches = !this.allBranches;
  }
}
