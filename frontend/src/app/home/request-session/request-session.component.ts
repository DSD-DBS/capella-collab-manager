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
  RepositoryService,
  Revisions,
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
  showSmallSpinner = false;
  creationSuccessful = false;

  history: Array<String> = ['Latest commit', 'Complete history'];
  isTag: boolean = false;

  repositoryFormGroup = new FormGroup(
    {
      workspaceSwitch: new FormControl(true),
      repository: new FormControl(''),
    },
    this.validateForm()
  );

  referenceDepthFormGroup = new FormGroup({
    reference: new FormControl('main'),
    historyDepth: new FormControl(this.history[0]),
  });

  get repository(): FormControl {
    return this.repositoryFormGroup.get('repository') as FormControl;
  }

  get reference(): FormControl {
    return this.referenceDepthFormGroup.get('reference') as FormControl;
  }

  get historyDepth(): FormControl {
    return this.referenceDepthFormGroup.get('historyDepth') as FormControl;
  }

  get workspaceSwitch(): FormControl {
    return this.repositoryFormGroup.get('workspaceSwitch') as FormControl;
  }

  @Input()
  repositories: Array<Repository> = [];

  chosenRepository: string = '';
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
    private repoUserService: RepositoryUserService,
    private repoService: RepositoryService
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
    if (
      this.repositoryFormGroup.valid &&
      (!this.workspaceSwitch.value || this.referenceDepthFormGroup.valid)
    ) {
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
        this.tags.includes(reference.value)
      ) {
        var depth = DepthType.LatestCommit;
      } else {
        var depth = DepthType.CompleteHistory;
      }
      var reference = this.reference.value;
      if (this.allBranches) {
        reference = '';
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
    this.showSmallSpinner = true;
    if (this.chosenRepository) this.chosenRepository = '';

    this.permissions = {};
    this.warnings = [];
    for (let repo of this.repositories) {
      if (repo.repository_name == event.value) {
        this.getRevisions(repo.repository_name);
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

  getRevisions(repository_name: string) {
    this.repoService.getRevisions(repository_name).subscribe(
      (revisions: Revisions) => {
        this.showSmallSpinner = false;
        this.branches = revisions.branches;
        this.tags = revisions.tags;
        this.referenceDepthFormGroup.controls['reference'].setValue(
          revisions.default
        );
        this.chosenRepository = repository_name;
      },
      (err) => {
        this.showSmallSpinner = false;
      },
      () => {
        this.showSmallSpinner = true;
      }
    );
  }

  changeIsTag(event: MatSelectChange) {
    if (this.tags.includes(event.value)) {
      this.isTag = true;
    } else {
      this.isTag = false;
    }
  }

  changeAllBranches() {
    this.allBranches = !this.allBranches;
    this.isTag = false;
  }
}
