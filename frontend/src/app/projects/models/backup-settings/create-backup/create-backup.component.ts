/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import {
  MatDialogRef as MatDialogRef,
  MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest } from 'rxjs';
import {
  BackupService,
  PostPipeline,
} from 'src/app/projects/models/backup-settings/service/backup.service';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';

@UntilDestroy()
@Component({
  selector: 'app-create-backup',
  templateUrl: './create-backup.component.html',
  styleUrls: ['./create-backup.component.css'],
})
export class CreateBackupComponent implements OnInit {
  t4cAndGitModelExists = false;

  constructor(
    public gitModelService: GitModelService,
    public t4cModelService: T4CModelService,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; modelSlug: string },
    private backupService: BackupService,
    private dialogRef: MatDialogRef<CreateBackupComponent>
  ) {}

  ngOnInit(): void {
    this.t4cModelService
      .listT4CModels(this.data.projectSlug, this.data.modelSlug)
      .subscribe();
    this.gitModelService.loadGitModels(
      this.data.projectSlug,
      this.data.modelSlug
    );

    combineLatest([
      this.gitModelService.gitModels,
      this.t4cModelService._t4cModels.asObservable(),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(
        ([gitModels, t4cModels]) =>
          (this.t4cAndGitModelExists = !!(
            gitModels?.length && t4cModels?.length
          ))
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
          this.data.projectSlug,
          this.data.modelSlug,
          createBackupformValue as PostPipeline
        )
        .subscribe(() => {
          this.dialogRef.close(true);
        });
    }
  }
}
