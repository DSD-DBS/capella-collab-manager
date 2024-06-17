/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgTemplateOutlet, AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatCheckbox } from '@angular/material/checkbox';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ToolModel } from 'src/app/openapi';
import {
  ModelRestrictions,
  ModelRestrictionsService,
  areRestrictionsEqual,
} from 'src/app/projects/models/model-restrictions/service/model-restrictions.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { MatCheckboxLoaderComponent } from '../../../helpers/skeleton-loaders/mat-checkbox-loader/mat-checkbox-loader.component';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-restrictions',
  templateUrl: './model-restrictions.component.html',
  styleUrls: ['./model-restrictions.component.css'],
  standalone: true,
  imports: [
    NgIf,
    FormsModule,
    ReactiveFormsModule,
    MatCheckboxLoaderComponent,
    NgTemplateOutlet,
    MatCheckbox,
    AsyncPipe,
  ],
})
export class ModelRestrictionsComponent implements OnInit {
  loading = false;

  private model?: ToolModel;
  private projectSlug?: string;

  constructor(
    public projectService: ProjectWrapperService,
    public modelService: ModelWrapperService,
    public toastService: ToastService,
    private modelRestrictionService: ModelRestrictionsService,
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
        if (model.restrictions) {
          this.updateRestrictionsForm(model.restrictions);
        }
      });

    this.projectService.project$.subscribe(
      (project) => (this.projectSlug = project?.slug),
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

    if (
      !this.model.restrictions ||
      areRestrictionsEqual(this.model.restrictions, restrictions)
    ) {
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
