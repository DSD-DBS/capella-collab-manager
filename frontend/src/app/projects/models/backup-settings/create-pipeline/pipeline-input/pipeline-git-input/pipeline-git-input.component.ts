/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
import { PluginTemplateInput } from 'src/app/plugins/store/service/plugin-store.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { GitModelService } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-pipeline-git-input',
  templateUrl: './pipeline-git-input.component.html',
  styleUrls: ['./pipeline-git-input.component.css'],
})
@UntilDestroy()
export class PipelineGitInputComponent {
  @Input()
  input?: PluginTemplateInput = undefined;

  selectedGitModelIDs?: number[] = undefined;

  @Output()
  inputFinished = new EventEmitter<GitModelInput>();

  get gitInput() {
    return this.input as PluginTemplateGitInput;
  }

  constructor(
    public gitModelService: GitModelService,
    private projectService: ProjectService,
    private modelService: ModelService,
  ) {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model]) => {
        this.gitModelService.loadGitModels(project.slug, model.slug);
      });
  }

  submitGitModel() {
    this.inputFinished.emit({ git_model_id: this.selectedGitModelIDs![0] });
  }
}

export type GitModelInput = {
  git_model_id: number;
};

export type PluginTemplateGitInput = PluginTemplateInput & {
  mapping: string;
  description: string;
};

export type PipelineGitInput = {
  git_model_id: number;
};
