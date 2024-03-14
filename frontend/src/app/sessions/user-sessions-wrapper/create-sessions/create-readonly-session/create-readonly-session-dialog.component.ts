/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { DialogRef } from '@angular/cdk/dialog';
import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  getPrimaryGitModel,
  Model,
} from 'src/app/projects/models/service/model.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { ModelOptions } from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-readonly-session/create-readonly-model-options/create-readonly-model-options.component';
import { ConnectionMethod } from 'src/app/settings/core/tools-settings/tool.service';

@UntilDestroy()
@Component({
  selector: 'create-readonly-session-dialog',
  templateUrl: './create-readonly-session-dialog.component.html',
  styleUrls: ['./create-readonly-session-dialog.component.css'],
})
export class CreateReadonlySessionDialogComponent implements OnInit {
  constructor(
    public sessionService: SessionService,
    @Inject(MAT_DIALOG_DATA)
    public data: {
      projectSlug: string;
      models: Model[];
      modelVersionId: number;
    },
    private router: Router,
    private toastService: ToastService,
    private dialog: DialogRef<CreateReadonlySessionDialogComponent>,
  ) {}

  form = new FormGroup({
    connectionMethodId: new FormControl<string | undefined>(
      undefined,
      Validators.required,
    ),
  });

  loading = false;

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

    if (this.modelOptions.length) {
      this.form.controls.connectionMethodId.setValue(
        this.modelOptions[0].model.tool.config.connection.methods[0].id,
      );
    }
  }

  selectedModelOptions(): ModelOptions[] {
    return this.modelOptions.filter((mo) => mo.include);
  }

  requestSession(): void {
    this.loading = true;
    const included = this.selectedModelOptions();

    if (included.length === 0) {
      this.toastService.showError(
        '',
        'Select at least one model to include in the session.',
      );
      return;
    }

    this.sessionService
      .createSession(
        this.modelOptions[0].model.tool.id,
        this.modelOptions[0].model.version!.id,
        this.form.controls.connectionMethodId.value!,
        'readonly',
        included.map((m) => {
          return {
            project_slug: this.data.projectSlug,
            model_slug: m.model.slug,
            git_model_id: m.primaryGitModel.id,
            revision: m.revision,
            deep_clone: m.deepClone,
          };
        }),
      )
      .subscribe({
        next: () => {
          this.dialog.close();
          this.router.navigateByUrl('/');
        },
        error: () => {
          this.loading = false;
        },
      });
  }

  getSelectedConnectionMethod(): ConnectionMethod {
    return this.modelOptions[0].model.tool.config.connection.methods.find(
      (method) => method.id === this.form.controls.connectionMethodId.value,
    )!;
  }
}
