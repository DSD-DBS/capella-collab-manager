/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { MatTooltip } from '@angular/material/tooltip';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, switchMap, tap } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ToolNature, ToolsService, ToolVersion } from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ToolWrapperService } from 'src/app/settings/core/tools-settings/tool.service';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-model-description',
  templateUrl: './model-description.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatError,
    MatSelect,
    MatOption,
    MatTooltip,
    MatButton,
    AsyncPipe,
  ],
})
export class ModelDescriptionComponent implements OnInit {
  form = new FormGroup({
    name: new FormControl<string>(''),
    description: new FormControl<string>(''),
    nature: new FormControl<number>(-1),
    version: new FormControl<number>(-1),
  });
  toolNatures?: ToolNature[];
  toolVersions?: ToolVersion[];

  public canDelete = false;

  private projectSlug?: string = undefined;
  private modelSlug?: string = undefined;

  constructor(
    public modelService: ModelWrapperService,
    public projectService: ProjectWrapperService,
    private toolWrapperService: ToolWrapperService,
    private toolService: ToolsService,
    public toastService: ToastService,
    private router: Router,
    private route: ActivatedRoute,
    private dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.modelService.model$
      .pipe(
        untilDestroyed(this),
        filter(Boolean),
        tap((model) => {
          this.modelSlug = model.slug;
          this.canDelete = !(
            model.git_models?.length || model.t4c_models?.length
          );

          this.form.controls.name.setAsyncValidators(
            this.modelService.asyncSlugValidator(model),
          );

          this.form.patchValue({
            name: model.name,
            description: model.description,
            nature: model.nature?.id,
            version: model.version?.id,
          });
        }),
        switchMap((model) => {
          return combineLatest([
            this.toolService.getToolNatures(model.tool.id),
            this.toolService.getToolVersions(model.tool.id),
          ]);
        }),
      )
      .subscribe((result: [ToolNature[], ToolVersion[]]) => {
        this.toolNatures = result[0];
        this.toolVersions = result[1];
      });

    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) => (this.projectSlug = project?.slug));
  }

  onSubmit(): void {
    if (this.form.value && this.modelSlug && this.projectSlug) {
      this.modelService
        .updateModel(this.projectSlug, this.modelSlug, {
          name: this.form.value.name || undefined,
          description: this.form.value.description || '',
          nature_id: this.form.value.nature || undefined,
          version_id: this.form.value.version || undefined,
        })
        .subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Model updated',
              `${this.modelSlug} has been updated`,
            );
            this.router.navigate(['../../..'], { relativeTo: this.route });
          },
        });
    }
  }

  deleteModel(): void {
    if (!(this.canDelete && this.modelSlug)) {
      return;
    }

    const modelSlug = this.modelSlug!;

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Delete Model',
        text: 'Do you really want to delete this model?',
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.modelService.deleteModel(this.projectSlug!, modelSlug).subscribe({
          next: () => {
            this.toastService.showSuccess(
              'Model deleted',
              `${modelSlug} has been deleted`,
            );
            this.router.navigate(['../../..'], { relativeTo: this.route });
          },
        });
      }
    });
  }
}
