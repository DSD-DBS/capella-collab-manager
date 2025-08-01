/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  inject,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, map, switchMap, tap } from 'rxjs';
import { SKIP_ERROR_HANDLING_CONTEXT } from 'src/app/general/error-handling/error-handling.interceptor';
import {
  ToolModel,
  ToolNature,
  ToolVersion,
  ToolsService,
  Tool,
} from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-init-model',
  templateUrl: './init-model.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatSelect,
    MatOption,
    MatButton,
    AsyncPipe,
  ],
})
export class InitModelComponent implements OnInit {
  projectService = inject(ProjectWrapperService);
  modelService = inject(ModelWrapperService);
  private toolsService = inject(ToolsService);

  @Output() create = new EventEmitter<{ created: boolean }>();
  @Input() asStepper?: boolean;

  toolVersions: ToolVersion[] = [];
  toolNatures: ToolNature[] = [];

  buttonDisabled = false;

  private projectSlug?: string = undefined;
  private modelSlug?: string = undefined;

  public form = new FormGroup({
    version: new FormControl<number | undefined>(
      undefined,
      Validators.required,
    ),
    nature: new FormControl<number | undefined>(undefined, Validators.required),
  });

  ngOnInit(): void {
    this.modelService.model$
      .pipe(
        untilDestroyed(this),
        filter(Boolean),
        tap((model) => {
          this.modelSlug = model.slug;
          if (model.version) {
            this.form.controls.version.patchValue(model.version.id);
          }
          if (model.nature) {
            this.form.controls.nature.patchValue(model.nature.id);
          }
        }),
        map((model: ToolModel) => model.tool),
        switchMap((tool: Tool) =>
          combineLatest([
            this.toolsService.getToolVersions(tool.id, undefined, undefined, {
              context: SKIP_ERROR_HANDLING_CONTEXT,
            }),
            this.toolsService.getToolNatures(tool.id, undefined, undefined, {
              context: SKIP_ERROR_HANDLING_CONTEXT,
            }),
          ]),
        ),
      )
      .subscribe((result: [ToolVersion[], ToolNature[]]) => {
        this.toolVersions = result[0];
        this.toolNatures = result[1];
      });

    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) => (this.projectSlug = project?.slug));
  }

  onSubmit(): void {
    if (this.form.valid && this.modelSlug && this.projectSlug) {
      this.modelService
        .setToolDetailsForModel(
          this.projectSlug!,
          this.modelSlug!,
          this.form.value.version!,
          this.form.value.nature!,
        )
        .subscribe(() => {
          this.create.emit({ created: true });
          this.buttonDisabled = true;
        });
    }
  }
}
