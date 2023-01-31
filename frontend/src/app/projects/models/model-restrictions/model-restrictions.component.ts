/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { filter, Subscription } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ModelRestrictions,
  ModelRestrictionsService,
} from 'src/app/projects/models/model-restrictions/service/model-restrictions.service';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-model-restrictions',
  templateUrl: './model-restrictions.component.html',
  styleUrls: ['./model-restrictions.component.css'],
})
export class ModelRestrictionsComponent implements OnInit {
  loading = false;
  modelServiceSubscription?: Subscription;

  private projectSlug?: string = undefined;

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

    this.modelServiceSubscription = this.modelService._model
      .pipe(filter(Boolean))
      .subscribe((model: Model) => {
        this.updateRestrictionsForm(model.restrictions);
      });

    this.projectService.project.subscribe(
      (project) => (this.projectSlug = project?.slug)
    );
  }

  private updateRestrictionsForm(restrictions: ModelRestrictions) {
    this.restrictionsForm.patchValue({
      pureVariants: restrictions.allow_pure_variants,
    });
  }

  private mapRestrictionsFormToToolModelRestrictionsObject(): ModelRestrictions {
    return {
      allow_pure_variants:
        this.restrictionsForm.controls.pureVariants.value || false,
    };
  }

  private patchRestrictions() {
    if (
      JSON.stringify(this.modelService.model?.restrictions) ===
      JSON.stringify(this.mapRestrictionsFormToToolModelRestrictionsObject())
    ) {
      return;
    }

    this.loading = true;
    this.modelRestrictionService
      .patchModelRestrictions(
        this.projectSlug!, // TODO: Check if we can actually use ! here
        this.modelService.model!.slug,
        this.mapRestrictionsFormToToolModelRestrictionsObject()
      )
      .subscribe((restrictions: ModelRestrictions) => {
        const newModel = this.modelService.model;
        newModel!.restrictions = restrictions;
        this.modelService._model.next(newModel);
        this.loading = false;
      });
  }
}
