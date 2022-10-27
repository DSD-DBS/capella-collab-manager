/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import {
  BackupService,
  PostEASEBackup,
} from 'src/app/projects/models/backup-settings/service/backup.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { T4CRepoService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Component({
  selector: 'app-create-backup',
  templateUrl: './create-backup.component.html',
  styleUrls: ['./create-backup.component.css'],
})
export class CreateBackupComponent {
  constructor(
    public gitModelService: GitModelService,
    public t4cRepoService: T4CRepoService,
    private easeBackupService: BackupService,
    private dialogRef: MatDialogRef<CreateBackupComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CreateEASEBackupData
  ) {}

  createGitBackupForm = new FormGroup({
    gitmodel: new FormControl('', Validators.required),
    t4cmodel: new FormControl('', Validators.required),
  });

  createGitBackup() {
    if (this.createGitBackupForm.valid) {
      this.easeBackupService
        .createBackup(
          this.data.project,
          this.createGitBackupForm.value as PostEASEBackup
        )
        .subscribe(() => {
          this.dialogRef.close(true);
        });
    }
  }
}

export interface CreateEASEBackupData {
  project: string;
}
