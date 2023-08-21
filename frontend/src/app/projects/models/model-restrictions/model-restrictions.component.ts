/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ModelRestrictions,
  ModelRestrictionsService,
  areRestrictionsEqual,
} from 'src/app/projects/models/model-restrictions/service/model-restrictions.service';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-restrictions',
  templateUrl: './model-restrictions.component.html',
  styleUrls: ['./model-restrictions.component.css'],
})
export class ModelRestrictionsComponent implements OnInit {
  loading = false;

  private model?: Model;
  private projectSlug?: string;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public toastService: ToastService,
    private modelRestrictionService: ModelRestrictionsService
  ) {}

  restrictionsForm = new FormGroup({
    pureVariants: new FormControl(false),
  });

  ngOnInit() {
    this.restrictionsForm.valueChanges.subscribe(() => {
      this.patchRestrictions();
    });

    this.modelService.model$
      .pipe(filter(Boolean), untilDestroyed(this))
      .subscribe((model) => {
        this.model = model;
        this.updateRestrictionsForm(model.restrictions);
      });

    this.projectService.project$.subscribe(
      (project) => (this.projectSlug = project?.slug)
    );
  }

  private updateRestrictionsForm(restrictions: ModelRestrictions) {
    this.restrictionsForm.patchValue({
      pureVariants: restrictions.allow_pure_variants,
    });
  }

  private patchRestrictions() {
    if (this.model === undefined || this.projectSlug === undefined) {
      return;
    }

    const projectSlug = this.projectSlug;
    const modelSlug = this.model.slug;
    const restrictions = this.mapRestrictionsFormToModelRestrictions();

    if (areRestrictionsEqual(this.model.restrictions, restrictions)) {
      return;
    }

    this.loading = true;
    this.modelRestrictionService
      .patchModelRestrictions(projectSlug, modelSlug, restrictions)
      .subscribe(() => {
        this.modelService.loadModelbySlug(modelSlug, projectSlug);
        this.loading = false;
      });
  }

  private mapRestrictionsFormToModelRestrictions(): ModelRestrictions {
    return {
      allow_pure_variants:
        this.restrictionsForm.controls.pureVariants.value || false,
    };
  }
}
