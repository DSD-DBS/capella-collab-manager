/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { filter } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-model-description',
  templateUrl: './model-description.component.html',
  styleUrls: ['./model-description.component.css'],
})
export class ModelDescriptionComponent implements OnInit {
  form = new FormControl<string>('');

  constructor(
    public modelService: ModelService,
    public projectService: ProjectService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.modelService._model.pipe(filter(Boolean)).subscribe((model) => {
      this.form.patchValue(model.description);
    });
  }

  onSubmit(): void {
    if (
      this.form.value &&
      this.modelService.model &&
      this.projectService.project
    ) {
      this.modelService
        .updateModelDescription(
          this.projectService.project.slug,
          this.modelService.model.slug,
          this.form.value || ''
        )
        .pipe(
          switchMap((_model) =>
            this.modelService.list(this.projectService.project!.slug)
          )
        )
        .subscribe((models) => {
          this.modelService._models.next(models);
          this.router.navigate(['../../..'], { relativeTo: this.route });
        });
    }
  }
}
