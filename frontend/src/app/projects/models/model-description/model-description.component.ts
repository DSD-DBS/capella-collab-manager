/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { combineLatest, filter, switchMap, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import {
  ToolNature,
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy({ checkProperties: true })
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

  public canDelete: boolean = false;

  private projectSlug?: string = undefined;
  private modelSlug?: string = undefined;

  constructor(
    public modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService,
    public toastService: ToastService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.modelService.model
      .pipe(filter(Boolean))
      .pipe(
        tap((model) => {
          this.modelSlug = model.slug;
          this.canDelete = !(
            model.git_models.length || model.t4c_models.length
          );

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

    this.projectService.project.subscribe(
      (project) => (this.projectSlug = project?.slug)
    );
  }

  onSubmit(): void {
    if (this.form.value && this.modelSlug && this.projectSlug) {
      this.modelService
        .updateModelDescription(this.projectSlug!, this.modelSlug!, {
          description: this.form.value.description || '',
          nature_id: this.form.value.nature || undefined,
          version_id: this.form.value.version || undefined,
        })
        .subscribe(() =>
          this.router.navigate(['../../..'], { relativeTo: this.route })
        );
    }
  }

  deleteModel(): void {
    if (
      !this.canDelete ||
      !this.modelSlug ||
      !window.confirm(`Do you really want to delete this model?`)
    ) {
      return;
    }

    const modelSlug = this.modelSlug;

    this.modelService.deleteModel(this.projectSlug!, modelSlug).subscribe({
      next: () => {
        this.toastService.showSuccess(
          'Model deleted',
          `${modelSlug} has been deleted`
        );
        this.router.navigate(['../../..'], { relativeTo: this.route });
      },
      error: () => {
        this.toastService.showError(
          'Model deletion failed',
          `${modelSlug} has not been deleted`
        );
      },
    });
  }
}
