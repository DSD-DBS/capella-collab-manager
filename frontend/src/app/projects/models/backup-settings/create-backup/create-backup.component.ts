/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import { MatDialogRef } from '@angular/material/dialog';
import {
  BackupService,
  PostPipeline,
} from 'src/app/projects/models/backup-settings/service/backup.service';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-create-backup',
  templateUrl: './create-backup.component.html',
  styleUrls: ['./create-backup.component.css'],
})
export class CreateBackupComponent {
  constructor(
    public gitModelService: GitModelService,
    public t4cModelService: T4CModelService,
    private backupService: BackupService,
    private dialogRef: MatDialogRef<CreateBackupComponent>,
    private projectService: ProjectService,
    private modelService: ModelService
  ) {
    this.t4cModelService
      .listT4CModels(
        this.projectService.project!.slug,
        this.modelService.model!.slug
      )
      .subscribe();

    this.gitModelService.loadGitModels(
      this.projectService.project!.slug,
      this.modelService.model!.slug
    );
  }

  createBackupForm = new FormGroup({
    gitmodel: new FormControl([], [this.listNotEmptyValidator()]),
    t4cmodel: new FormControl([], [this.listNotEmptyValidator()]),
    configuration: new FormGroup({
      includeCommitHistory: new FormControl(false),
      runNightly: new FormControl(true),
    }),
  });

  listNotEmptyValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (!control.value.length) {
        return { listNotEmpty: true };
      }
      return null;
    };
  }

  createGitBackup() {
    if (this.createBackupForm.valid) {
      const formValue = this.createBackupForm.value;
      const createBackupformValue: PostPipeline = {
        gitmodelId: formValue.gitmodel![0],
        t4cmodelId: formValue.t4cmodel![0],
        includeCommitHistory: formValue.configuration!.includeCommitHistory!,
        runNightly: formValue.configuration!.runNightly!,
      };
      this.backupService
        .createBackup(
          this.projectService.project!.slug,
          this.modelService.model!.slug,
          createBackupformValue as unknown as PostPipeline
        )
        .subscribe(() => {
          this.dialogRef.close(true);
        });
    }
  }

  t4cModelAndGitModelExists(): boolean {
    return !!(
      this.t4cModelService.t4cModels?.length &&
      this.gitModelService._gitModels.value?.length
    );
  }
}
