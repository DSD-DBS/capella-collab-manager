/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { ProjectUser, Session, Warnings } from 'src/app/schemes';
import { MatSelectChange } from '@angular/material/select';
import { ProjectService } from 'src/app/services/project/project.service';
import {
  GitModelService,
  Revisions,
} from 'src/app/services/modelsources/git-model/git-model.service';

import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import {
  DepthType,
  SessionService,
} from 'src/app/services/session/session.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';

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

  referenceDepthFormGroup = new FormGroup(
    {
      reference: new FormControl(''),
      historyDepth: new FormControl(this.history[0]),
    },
    Validators.required
  );

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
  ownProjects: Array<ProjectUser> = [];

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
    private projectService: ProjectService,
    private gitModelService: GitModelService,
    private toastService: ToastService
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
        this.tags.includes(this.reference.value)
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

    this.warnings = [];
    for (let project of this.ownProjects) {
      if (project.project_name == event.value) {
        if (project.warnings.includes('NO_GIT_MODEL_DEFINED')) {
          this.toastService.showError(
            'This project has no assigned read-only model and therefore, a readonly-session cannot be created. Please contact your project lead.',
            ''
          );
          this.showSmallSpinner = false;
        } else {
          this.getRevisions(project.project_name);
        }
        this.warnings = project.warnings;
        return;
      }
    }
  }

  getRevisions(repository_name: string) {
    this.showSmallSpinner = true;
    this.gitModelService.getRevisions(repository_name).subscribe({
      next: (revisions: Revisions) => {
        this.branches = revisions.branches;
        this.tags = revisions.tags;
        this.referenceDepthFormGroup.controls['reference'].setValue(
          revisions.default
        );
        this.chosenRepository = repository_name;
      },
      error: () => {
        this.showSmallSpinner = false;
      },
      complete: () => {
        this.showSmallSpinner = false;
      },
    });
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
