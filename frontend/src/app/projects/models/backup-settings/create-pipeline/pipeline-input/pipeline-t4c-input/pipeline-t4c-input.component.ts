/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
import { PluginTemplateInput } from 'src/app/plugins/store/service/plugin-store.service';
import { T4CModelService } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-pipeline-t4c-input',
  templateUrl: './pipeline-t4c-input.component.html',
  styleUrls: ['./pipeline-t4c-input.component.css'],
})
@UntilDestroy()
export class PipelineT4CInputComponent {
  @Input()
  input?: PluginTemplateInput = undefined;

  selectedT4CModelIDs?: number[] = undefined;

  @Output()
  inputFinished = new EventEmitter<T4CModelInput>();

  get t4cInput() {
    return this.input as PluginTemplateT4CInput;
  }

  constructor(
    public t4cModelService: T4CModelService,
    private projectService: ProjectService,
    private modelService: ModelService,
  ) {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model]) => {
        this.t4cModelService.loadT4CModels(project.slug, model.slug);
      });
  }

  submitGitModel() {
    this.inputFinished.emit({ t4c_model_id: this.selectedT4CModelIDs![0] });
  }
}

export type T4CModelInput = {
  t4c_model_id: number;
};

export type PluginTemplateT4CInput = PluginTemplateInput & {
  mapping: string;
  description: string;
};

export type PipelineT4CInput = {
  t4c_model_id: number;
};
