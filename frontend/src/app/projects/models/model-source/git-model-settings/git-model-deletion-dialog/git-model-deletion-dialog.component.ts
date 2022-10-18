/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import {
  GitModel,
  GitModelService,
} from 'src/app/services/modelsources/git-model/git-model.service';

@Component({
  selector: 'app-git-model-deletion-dialog',
  templateUrl: './git-model-deletion-dialog.component.html',
  styleUrls: ['./git-model-deletion-dialog.component.css'],
})
export class GitModelDeletionDialogComponent {
  constructor(
    private gitModelService: GitModelService,
    public dialogRef: MatDialogRef<GitModelDeletionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public input: GitModelDeletionDialogInput
  ) {}

  unassignGitModel() {
    this.gitModelService
      .unassignGitRepositoriesFromRepository(
        this.input.repository,
        this.input.model.id
      )
      .subscribe(() => {
        this.dialogRef.close(true);
      });
  }
}

export interface GitModelDeletionDialogInput {
  model: GitModel;
  repository: string;
}
