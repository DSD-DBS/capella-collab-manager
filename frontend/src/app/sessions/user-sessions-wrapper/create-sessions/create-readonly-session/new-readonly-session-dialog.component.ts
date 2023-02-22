/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';

import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { map } from 'rxjs';

import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';
import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { ModelOptions } from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-readonly-session/new-readonly-model-options/new-readonly-model-options.component';

@UntilDestroy()
@Component({
  selector: 'new-readonly-session-dialog',
  templateUrl: './new-readonly-session-dialog.component.html',
  styleUrls: ['./new-readonly-session-dialog.component.css'],
})
export class NewReadonlySessionDialogComponent implements OnInit {
  constructor(
    public sessionService: SessionService,
    public modelService: ModelService,
    private router: Router,
    @Inject(MAT_DIALOG_DATA) public data: { projectSlug: string; model: Model }
  ) {}

  private _modelOptions: ModelOptions[] = [];

  get modelOptions(): ModelOptions[] {
    return this._modelOptions;
  }

  ngOnInit(): void {
    this.modelService.models
      .pipe(
        untilDestroyed(this),
        map((models) =>
          models?.filter(
            (model) => model.version?.id === this.data.model.version?.id
          )
        )
      )
      .subscribe((models) => {
        this._modelOptions = [];
        models?.forEach((model) => {
          const primaryGitModel = getPrimaryGitModel(model);
          if (!primaryGitModel) {
            return;
          }

          this._modelOptions.push({
            model: model,
            primary_git_model: primaryGitModel,
            include: model.id === this.data.model.id,
            revision: primaryGitModel.revision,
            deepClone: false,
          });
        });
      });

    this.modelService.loadModels(this.data.projectSlug);
  }

  requestSession(): void {
    let included = this._modelOptions.filter((mo) => mo.include);

    if (!included) {
      return;
    }

    this.sessionService
      .createReadonlySession(
        this.data.projectSlug,
        included.map((m) => {
          return {
            model_slug: m.model.slug,
            git_model_id: m.primary_git_model.id,
            revision: m.revision,
            deep_clone: m.deepClone,
          };
        })
      )
      .subscribe(() => {
        this.router.navigateByUrl('/');
      });
  }
}

function getPrimaryGitModel(model: Model): GetGitModel | undefined {
  return model.git_models.find((gitModel) => gitModel.primary);
}
