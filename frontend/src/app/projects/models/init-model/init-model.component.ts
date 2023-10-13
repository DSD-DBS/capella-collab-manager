/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, map, switchMap, tap } from 'rxjs';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import {
  Tool,
  ToolService,
  ToolNature,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { GitModelService } from '../../project-detail/model-overview/model-detail/git-model.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-init-model',
  templateUrl: './init-model.component.html',
  styleUrls: ['./init-model.component.css'],
})
export class InitModelComponent implements OnInit {
  @Output() create = new EventEmitter<{ created: boolean }>();
  @Input() asStepper?: boolean;

  toolVersions: ToolVersion[] = [];
  toolNatures: ToolNature[] = [];

  buttonDisabled = false;

  private projectSlug?: string = undefined;
  private modelSlug?: string = undefined;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public gitModelService: GitModelService,
    public toolService: ToolService,
  ) {}

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
        map((model: Model) => model.tool),
        switchMap((tool: Tool) =>
          combineLatest([
            this.toolService.getVersionsForTool(tool.id),
            this.toolService.getNaturesForTool(tool.id),
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
