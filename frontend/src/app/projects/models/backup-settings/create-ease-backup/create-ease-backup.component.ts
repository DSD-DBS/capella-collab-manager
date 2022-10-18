/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import {
  EASEBackupService,
  PostEASEBackup,
} from 'src/app/services/backups/ease/easebackup.service';
import { GitModelService } from 'src/app/services/modelsources/git-model/git-model.service';
import { T4CRepoService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Component({
  selector: 'app-create-ease-backup',
  templateUrl: './create-ease-backup.component.html',
  styleUrls: ['./create-ease-backup.component.css'],
})
export class CreateEASEBackupComponent {
  constructor(
    public gitModelService: GitModelService,
    public t4cRepoService: T4CRepoService,
    private easeBackupService: EASEBackupService,
    private dialogRef: MatDialogRef<CreateEASEBackupComponent>,
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
