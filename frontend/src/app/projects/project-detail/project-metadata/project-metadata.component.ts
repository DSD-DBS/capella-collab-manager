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
import { FormControl } from '@angular/forms';
import { ToastService } from 'src/app/toast/toast.service';
import {
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

  public updateDescriptionForm = new FormControl();

  constructor(
    private toastService: ToastService,
    private projectService: ProjectService
  ) {}

  ngOnChanges(_changes: SimpleChanges): void {
    this.updateDescriptionForm.patchValue(this.project.description);
  }

  updateDescription() {
    if (this.updateDescriptionForm.valid) {
      this.projectService
        .updateDescription(this.project.name, this.updateDescriptionForm.value)
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
