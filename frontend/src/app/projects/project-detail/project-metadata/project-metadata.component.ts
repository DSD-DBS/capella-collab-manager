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
    name: new FormControl<string>('', Validators.required),
    description: new FormControl<string>('', Validators.required),
  });

  constructor(
    private toastService: ToastService,
    private projectService: ProjectService
  ) {}

  ngOnChanges(_changes: SimpleChanges): void {
    this.form.patchValue(this.project);
  }

  updateDescription() {
    if (this.form.valid) {
      this.projectService
        .updateProject(this.project.slug, this.form.value as PatchProject)
        .subscribe((project) => {
          this.projectService._project.next(project);
          this.toastService.showSuccess(
            'Description updated for project ' + this.project.name,
            "Updated to '" + project.description + "'"
          );
        });
    }
  }
}
