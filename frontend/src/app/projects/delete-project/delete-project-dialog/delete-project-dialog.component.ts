/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DeleteProjectComponent } from 'src/app/projects/delete-project/delete-project.component';
import { StagedProjectsOverviewComponent } from 'src/app/settings/requests/staged-projects-overview/staged-projects-overview.component';
@Component({
  selector: 'app-delete-project-dialog',
  templateUrl: './delete-project-dialog.component.html',
  styleUrls: ['./delete-project-dialog.component.css'],
})
export class DeleteProjectDialogComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<DeleteProjectComponent>,
    public dialogRefOverview: MatDialogRef<StagedProjectsOverviewComponent>,
    @Inject(MAT_DIALOG_DATA)
    public data: { project_name: string; overview: boolean }
  ) {}
  ngOnInit(): void {}
}
