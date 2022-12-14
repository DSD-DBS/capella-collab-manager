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
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import slugify from 'slugify';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  PatchProject,
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';

@Component({
  selector: 'app-project-metadata',
  templateUrl: './project-metadata.component.html',
  styleUrls: ['./project-metadata.component.css'],
})
export class ProjectMetadataComponent implements OnChanges {
  @Input() project!: Project;
  @Output() changeProject = new EventEmitter<Project>();

  public form = new FormGroup({
    name: new FormControl<string>('', [
      Validators.required,
      this.slugValidator(),
    ]),
    description: new FormControl<string>(''),
  });

  constructor(
    private toastService: ToastService,
    private projectService: ProjectService,
    private router: Router
  ) {}

  ngOnChanges(_changes: SimpleChanges): void {
    this.projectService.list().subscribe();
    this.form.patchValue(this.project);
  }

  updateDescription() {
    if (this.form.valid) {
      this.projectService
        .updateProject(this.project.slug, this.form.value as PatchProject)
        .subscribe((project) => {
          this.projectService._project.next(project);
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

  slugValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const slug = slugify(control.value, { lower: true });
      if (
        this.projectService.projects
          ?.map((project) => project.slug)
          .filter((slug) => slug !== this.projectService.project?.slug)
          .includes(slug)
      ) {
        return { uniqueSlug: { value: slug } };
      }
      return null;
    };
  }

  get newSlug(): string | null {
    return this.form.value.name ? slugify(this.form.value.name) : null;
  }
}
