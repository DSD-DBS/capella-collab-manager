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
import { UntilDestroy } from '@ngneat/until-destroy';
import { combineLatest } from 'rxjs';
import {
  BackupService,
  PostPipeline,
} from 'src/app/projects/models/backup-settings/service/backup.service';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@UntilDestroy({ checkProperties: true })
@Component({
  selector: 'app-create-backup',
  templateUrl: './create-backup.component.html',
  styleUrls: ['./create-backup.component.css'],
})
export class CreateBackupComponent {
  t4cAndGitModelExists = false;

  private projectSlug?: string = undefined; // TODO: Check if I can removed them somehow
  private modelSlug?: string = undefined; // TODO: Check if I can removed them somehow

  constructor(
    public gitModelService: GitModelService,
    public t4cModelService: T4CModelService,
    private backupService: BackupService,
    private dialogRef: MatDialogRef<CreateBackupComponent>,
    private projectService: ProjectService,
    private modelService: ModelService
  ) {
    // TODO: Try to further simplify when model service is also refactored
    combineLatest([
      this.projectService.project,
      this.modelService._model.asObservable(),
    ]).subscribe(([project, model]) => {
      this.projectSlug = project?.slug;
      this.modelSlug = model?.slug;

      this.t4cModelService
        .listT4CModels(project!.slug, model!.slug)
        .subscribe();
      this.gitModelService.loadGitModels(project!.slug, model!.slug);
    });

    combineLatest([
      this.gitModelService.gitModels,
      this.t4cModelService._t4cModels.asObservable(),
    ]).subscribe(
      ([gitModels, t4cModels]) =>
        (this.t4cAndGitModelExists = !!(gitModels?.length && t4cModels?.length))
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
    // TODO: Check if model slug and project slug is needed here
    if (this.createBackupForm.valid && this.modelSlug && this.projectSlug) {
      const formValue = this.createBackupForm.value;
      const createBackupformValue: PostPipeline = {
        gitmodelId: formValue.gitmodel![0],
        t4cmodelId: formValue.t4cmodel![0],
        includeCommitHistory: formValue.configuration!.includeCommitHistory!,
        runNightly: formValue.configuration!.runNightly!,
      };
      this.backupService
        .createBackup(
          this.projectSlug,
          this.modelSlug,
          createBackupformValue as PostPipeline
        )
        .subscribe(() => {
          this.dialogRef.close(true);
        });
    }
  }
}
