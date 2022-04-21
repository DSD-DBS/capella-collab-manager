// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/services/modelsources/t4c-repos/t4c-repo.service';

@Component({
  selector: 'app-project-deletion-dialog',
  templateUrl: './project-deletion-dialog.component.html',
  styleUrls: ['./project-deletion-dialog.component.css'],
})
export class ProjectDeletionDialogComponent implements OnInit {
  constructor(
    private projectService: T4CRepoService,
    public dialogRef: MatDialogRef<ProjectDeletionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public project: T4CRepository
  ) {}

  ngOnInit(): void {}

  removeProject(): void {
    this.projectService
      .deleteRepositoryProject(this.project.repository_name, this.project.id)
      .subscribe(() => {
        this.dialogRef.close(true);
      });
  }
}
