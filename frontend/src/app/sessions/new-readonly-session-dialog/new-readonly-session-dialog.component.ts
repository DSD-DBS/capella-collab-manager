/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';

import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Router } from '@angular/router';

import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { GitService } from 'src/app/services/git/git.service';
import { Model, ModelService } from 'src/app/services/model/model.service';
import { Project } from 'src/app/services/project/project.service';
import { SessionService } from 'src/app/services/session/session.service';
import { ModelOptions } from 'src/app/sessions/new-readonly-session-dialog/new-readonly-model-options.component';

@Component({
  selector: 'new-readonly-session-dialog',
  templateUrl: './new-readonly-session-dialog.component.html',
  styleUrls: ['./new-readonly-session-dialog.component.css'],
})
export class NewReadonlySessionDialogComponent implements OnInit {
  constructor(
    public sessionService: SessionService,
    private gitService: GitService,
    private router: Router,
    public modelService: ModelService,
    @Inject(MAT_DIALOG_DATA) public data: { project: Project; model: Model }
  ) {}

  private model_options: ModelOptions[] = [];

  get modelOptions(): ModelOptions[] {
    return this.model_options;
  }

  ngOnInit(): void {
    this.modelService.getModels(this.data.project.slug).subscribe((models) => {
      models
        .filter((m) => m.version?.id == this.data.model.version?.id)
        .forEach((model) => {
          const primary_git_model = get_primary_git_model(model);
          if (!primary_git_model) {
            return;
          }

          this.model_options.push({
            model: model,
            primary_git_model: primary_git_model,
            include: model.id === this.data.model.id,
            revision: primary_git_model.revision,
            deepClone: false,
          });
        });
    });
  }

  requestSession(): void {
    let included = this.model_options.filter((mo) => mo.include);

    if (!included) {
      return;
    }

    this.sessionService
      .createReadonlySession(this.data.project.slug, this.data.model.slug)
      .subscribe(() => {
        this.router.navigateByUrl('/');
      });
  }
}

function get_primary_git_model(model: Model): GetGitModel | undefined {
  return model.git_models.find((gm) => gm.primary);
}
