/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { combineLatest, filter, switchMap, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/services/project/project.service';
import {
  ToolNature,
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';

@Component({
  selector: 'app-model-description',
  templateUrl: './model-description.component.html',
  styleUrls: ['./model-description.component.css'],
})
export class ModelDescriptionComponent implements OnInit {
  form = new FormGroup({
    description: new FormControl<string>(''),
    nature: new FormControl<number>(-1),
    version: new FormControl<number>(-1),
  });
  toolNatures?: ToolNature[];
  toolVersions?: ToolVersion[];

  constructor(
    public modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService,
    public toastService: ToastService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.modelService._model
      .pipe(filter(Boolean))
      .pipe(
        tap((model) => {
          this.form.patchValue({
            description: model.description,
            nature: model.nature?.id,
            version: model.version?.id,
          });
        }),
        switchMap((model) => {
          return combineLatest([
            this.toolService.getNaturesForTool(model.tool.id),
            this.toolService.getVersionsForTool(model.tool.id),
          ]);
        })
      )
      .subscribe((result: [ToolNature[], ToolVersion[]]) => {
        this.toolNatures = result[0];
        this.toolVersions = result[1];
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
          {
            description: this.form.value.description || '',
            nature_id: this.form.value.nature || undefined,
            version_id: this.form.value.version || undefined,
          }
        )
        .pipe(
          switchMap((_model) =>
            this.modelService.getModels(this.projectService.project!.slug)
          )
        )
        .subscribe((models) => {
          this.modelService._models.next(models);
          this.router.navigate(['../../..'], { relativeTo: this.route });
        });
    }
  }

  get canDelete(): boolean {
    const model = this.modelService.model!;
    return !(model.git_models.length || model.t4c_models.length);
  }

  deleteModel(): void {
    const model = this.modelService.model!;

    if (
      !this.canDelete ||
      !window.confirm(`Do you really want to delete this model?`)
    ) {
      return;
    }

    this.modelService
      .deleteModel(this.projectService.project?.slug!, model)
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'Model deleted',
            `${model.name} has been deleted`
          );
          this.router.navigate(['../../..'], { relativeTo: this.route });
        },
        error: () => {
          this.toastService.showError(
            'Model deletion failed',
            `${model.name} has not been deleted`
          );
        },
      });
  }
}
