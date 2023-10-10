/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import {
  getPrimaryGitModel,
  Model,
} from 'src/app/projects/models/service/model.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { ModelOptions } from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-readonly-session/create-readonly-model-options/create-readonly-model-options.component';

@UntilDestroy()
@Component({
  selector: 'create-readonly-session-dialog',
  templateUrl: './create-readonly-session-dialog.component.html',
  styleUrls: ['./create-readonly-session-dialog.component.css'],
})
export class CreateReadonlySessionDialogComponent implements OnInit {
  constructor(
    public sessionService: SessionService,

    private router: Router,
    @Inject(MAT_DIALOG_DATA)
    public data: {
      projectSlug: string;
      models: Model[];
      modelVersionId: number;
    },
  ) {}

  modelOptions: ModelOptions[] = [];

  ngOnInit(): void {
    const filteredModels = this.data.models.filter(
      (model) => model.version?.id === this.data.modelVersionId,
    );

    for (const model of filteredModels) {
      const primaryGitModel = getPrimaryGitModel(model);
      if (!primaryGitModel) {
        continue;
      }

      this.modelOptions.push({
        model: model,
        primaryGitModel: primaryGitModel,
        revision: primaryGitModel.revision,
        include: false,
        deepClone: false,
      });
    }
  }

  requestSession(): void {
    const included = this.modelOptions.filter((mo) => mo.include);

    if (!included) {
      return;
    }

    this.sessionService
      .createReadonlySession(
        this.data.projectSlug,
        included.map((m) => {
          return {
            model_slug: m.model.slug,
            git_model_id: m.primaryGitModel.id,
            revision: m.revision,
            deep_clone: m.deepClone,
          };
        }),
      )
      .subscribe(() => {
        this.router.navigateByUrl('/');
      });
  }
}
