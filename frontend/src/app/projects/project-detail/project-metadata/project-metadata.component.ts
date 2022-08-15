// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ToastService } from 'src/app/toast/toast.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-project-metadata',
  templateUrl: './project-metadata.component.html',
  styleUrls: ['./project-metadata.component.css'],
})
export class ProjectMetadataComponent implements OnInit {
  @Input()
  project_slug = '';

  constructor(
    public projectService: ProjectService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.projectService.getSlug(this.project_slug).subscribe((project) => {
      this.projectService.project = project;
    });
  }

  updateDescriptionForm = new FormControl(
    this.projectService.project?.description
  );

  updateDescription() {
    if (this.updateDescriptionForm.valid && this.projectService.project) {
      this.projectService
        .updateDescription(
          this.projectService.project.name,
          this.updateDescriptionForm.value
        )
        .subscribe({
          next: (res) => {
            this.updateDescriptionForm.reset();
            this.updateDescriptionForm.setValue(res.description);
            this.toastService.showSuccess(
              'Description updated for project ' +
                this.projectService.project?.name,
              "Updated to '" + res.description + "'"
            );
          },
          error: () => {},
        });
    }
  }
}
