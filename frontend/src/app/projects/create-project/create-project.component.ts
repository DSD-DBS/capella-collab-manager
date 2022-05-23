// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatStepper } from '@angular/material/stepper';
import { Router } from '@angular/router';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-create-project',
  templateUrl: './create-project.component.html',
  styleUrls: ['./create-project.component.css'],
})
export class CreateProjectComponent implements OnInit {
  nextLoading = false;
  createProjectForm = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
    editingMode: new FormControl('git'),
    type: new FormControl('project'),
  });

  get name(): FormControl {
    return this.createProjectForm.get('name') as FormControl;
  }

  constructor(private projectService: ProjectService, private router: Router) {}

  ngOnInit(): void {}

  createProject(stepper: MatStepper): void {
    if (this.createProjectForm.valid) {
      this.projectService.createProject(this.name.value).subscribe(() => {
        this.projectService.refreshProjects();
        stepper.next();
      });
    }
  }
}
