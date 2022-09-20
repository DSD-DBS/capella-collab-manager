/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { filter, switchMap } from 'rxjs';
import { DeleteProjectDialogComponent } from 'src/app/projects/delete-project/delete-project-dialog/delete-project-dialog.component';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';
@Component({
  selector: 'app-delete-project',
  templateUrl: './delete-project.component.html',
  styleUrls: ['./delete-project.component.css'],
})
export class DeleteProjectComponent implements OnInit {
  @Input() project!: Project;

  constructor(
    private dialog: MatDialog,
    private projectService: ProjectService,
    private router: Router
  ) {}

  ngOnInit(): void {}

  openDeleteDialog() {
    const deleteProjectDialog = this.dialog.open(DeleteProjectDialogComponent, {
      data: { project_name: this.project.name, overview: false },
    });
    deleteProjectDialog
      .afterClosed()
      .pipe(
        filter(Boolean),
        switchMap(() => this.projectService.deleteProject(this.project.slug))
      )
      .subscribe((_) => {
        this.projectService._project.next(undefined);
        this.router.navigateByUrl('/projects');
      });
  }
}
