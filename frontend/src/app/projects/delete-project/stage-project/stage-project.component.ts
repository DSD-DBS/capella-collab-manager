/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { filter, switchMap } from 'rxjs';
import { StageProjectDialogComponent } from 'src/app/projects/delete-project/stage-project-dialog/stage-project-dialog.component';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';
@Component({
  selector: 'app-stage-project',
  templateUrl: './stage-project.component.html',
  styleUrls: ['./stage-project.component.css'],
})
export class StageProjectComponent implements OnInit {
  @Input() project!: Project;

  constructor(
    private dialog: MatDialog,
    private projectService: ProjectService,
    private router: Router
  ) {}
  ngOnInit(): void {}

  openStageDialog() {
    if (this.project.staged_by) {
      this.unstage();
    } else {
      const stageProjectDialog = this.dialog.open(StageProjectDialogComponent, {
        data: this.project.name,
      });
      stageProjectDialog
        .afterClosed()
        .pipe(
          filter(Boolean),
          switchMap(() => {
            return this.projectService.stageForProjectDeletion(
              this.project.slug
            );
          })
        )
        .subscribe((_) => this.router.navigateByUrl('/projects'));
    }
  }

  unstage() {
    this.projectService.unstageProject(this.project.slug).subscribe({
      next: this.projectService._project.next.bind(
        this.projectService._project
      ),
    });
  }
}
