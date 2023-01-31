/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
} from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import slugify from 'slugify';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { asyncProjectSlugValidator } from 'src/app/helpers/validators/slug-validator';
import { ModelService } from 'src/app/projects/models/service/model.service';
import {
  PatchProject,
  Project,
  ProjectService,
} from '../../service/project.service';

@Component({
  selector: 'app-project-metadata',
  templateUrl: './project-metadata.component.html',
  styleUrls: ['./project-metadata.component.css'],
})
export class ProjectMetadataComponent implements OnChanges {
  @Input() project!: Project;
  @Output() changeProject = new EventEmitter<Project>();

  constructor(
    private toastService: ToastService,
    private projectService: ProjectService,
    private modelService: ModelService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  public form = new FormGroup({
    name: new FormControl<string>(
      '',
      [Validators.required],
      [asyncProjectSlugValidator(this.projectService.projects)]
    ),
    description: new FormControl<string>(''),
  });

  ngOnChanges(_changes: SimpleChanges): void {
    this.projectService.loadProjects();
    this.form.patchValue(this.project);
  }

  updateDescription() {
    if (this.form.valid) {
      this.projectService
        .updateProject(this.project.slug, this.form.value as PatchProject)
        .subscribe((project) => {
          this.router.navigateByUrl(`/project/${project.slug}`);
          this.toastService.showSuccess(
            'Project updated',
            `The new name is: '${project.name}' and the new description is '${
              project.description || ''
            }'`
          );
        });
    }
  }

  get newSlug(): string | null {
    return this.form.value.name ? slugify(this.form.value.name) : null;
  }

  get canDelete(): boolean {
    return !this.modelService.models?.length;
  }

  deleteProject(): void {
    const project = this.project;

    if (
      !this.canDelete ||
      !window.confirm(
        `Do you really want to delete this project? All assigned users will lose access to it! The project cannot be restored!`
      )
    ) {
      return;
    }

    this.projectService.deleteProject(project.slug).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Project deleted',
          `${project.name} has been deleted`
        );
        this.router.navigate(['../../projects'], { relativeTo: this.route });
      },
      error: () => {
        this.toastService.showError(
          'Project deletion failed',
          `${project.name} has not been deleted`
        );
      },
    });
  }
}
