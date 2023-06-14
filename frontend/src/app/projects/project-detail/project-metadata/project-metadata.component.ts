/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectUserService } from 'src/app/projects/project-detail/project-users/service/project-user.service';
import { Project, ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-project-metadata',
  templateUrl: './project-metadata.component.html',
  styleUrls: ['./project-metadata.component.css'],
})
export class ProjectMetadataComponent {
  project?: Project;
  canDelete = false;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public projectUserService: ProjectUserService,
    private toastService: ToastService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.projectService.project
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => {
        this.project = project;
      });

    this.modelService.models
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((models) => (this.canDelete = !models.length));
  }

  deleteProject(): void {
    if (
      !this.canDelete ||
      !this.project ||
      !window.confirm(
        `Do you really want to delete this project? All assigned users will lose access to it! The project cannot be restored!`
      )
    ) {
      return;
    }

    const projectSlug: string = this.project.slug;

    this.projectService.deleteProject(projectSlug).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Project deleted',
          `${projectSlug} has been deleted`
        );
        this.router.navigate(['../../projects'], { relativeTo: this.route });
      },
      error: () => {
        this.toastService.showError(
          'Project deletion failed',
          `${projectSlug} has not been deleted`
        );
      },
    });
  }
}
