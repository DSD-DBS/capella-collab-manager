/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Component({
  selector: 't4c-repo-deletion-dialog-dialog',
  templateUrl: './t4c-repo-deletion-dialog.component.html',
  styleUrls: ['./t4c-repo-deletion-dialog.component.css'],
})
export class T4CRepoDeletionDialogComponent implements OnInit {
  constructor(
    private repoService: T4CRepoService,
    public dialogRef: MatDialogRef<T4CRepoDeletionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public repo: T4CRepository
  ) {}

  ngOnInit(): void {}

  remoteRepository(): void {
    this.repoService
      .deleteRepository(this.repo.instance_id, this.repo.name)
      .subscribe(() => {
        this.dialogRef.close(true);
      });
  }
}
