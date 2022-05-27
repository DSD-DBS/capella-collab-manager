// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';
import { FormControl, Validators } from '@angular/forms';
import { ToastService } from 'src/app/toast/toast.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-project-metadata',
  templateUrl: './project-metadata.component.html',
  styleUrls: ['./project-metadata.component.css'],
})
export class ProjectMetadataComponent implements OnInit {
  @Input()
  project = '';

  constructor(
    public projectService: ProjectService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {}

  updateDescriptionForm = new FormControl(
    this.projectService.project?.description,
    Validators.required
  );

  updateDescription() {
    if (this.updateDescriptionForm.valid) {
      this.projectService
        .updateDescription(this.project, this.updateDescriptionForm.value)
        .subscribe({
          next: (res) => {
            this.updateDescriptionForm.reset();
            this.updateDescriptionForm.setValue(res.description);
            this.projectService.project = res;
            this.toastService.showSuccess(
              'Description updated for project ' + this.project,
              "Updated to '" + res.description + "'"
            );
          },
          error: (res) => {},
        });
    }
  }
}
