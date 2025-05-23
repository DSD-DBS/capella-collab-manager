/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { DialogRef } from '@angular/cdk/dialog';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogClose } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatRadioButton, MatRadioGroup } from '@angular/material/radio';
import { Router } from '@angular/router';
import { UntilDestroy } from '@ngneat/until-destroy';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { SessionType, Tool, ToolModel, ToolVersion } from 'src/app/openapi';
import { getPrimaryGitModel } from 'src/app/projects/models/service/model.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import {
  CreateReadonlyModelOptionsComponent,
  ModelOptions,
} from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-readonly-session/create-readonly-model-options/create-readonly-model-options.component';
import { ConnectionMethod } from 'src/app/settings/core/tools-settings/tool.service';

@UntilDestroy()
@Component({
  selector: 'create-readonly-session-dialog',
  templateUrl: './create-readonly-session-dialog.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatRadioGroup,
    MatRadioButton,
    CreateReadonlyModelOptionsComponent,
    MatButton,
    MatDialogClose,
    MatIconModule,
  ],
})
export class CreateReadonlySessionDialogComponent implements OnInit {
  sessionService = inject(SessionService);
  data = inject<{
    projectSlug: string;
    models: ToolModel[];
    tool: Tool;
    toolVersion: ToolVersion;
  }>(MAT_DIALOG_DATA);
  private router = inject(Router);
  private toastService = inject(ToastService);
  private dialog =
    inject<DialogRef<CreateReadonlySessionDialogComponent>>(DialogRef);

  maxNumberOfModels?: number;
  connectionMethods: ConnectionMethod[] = [];

  form = new FormGroup({
    connectionMethodId: new FormControl<string | undefined>(
      undefined,
      Validators.required,
    ),
  });

  loading = false;

  modelOptions: ModelOptions[] = [];

  ngOnInit(): void {
    this.connectionMethods = this.data.tool.config.connection.methods;
    this.maxNumberOfModels =
      this.data.tool.config.provisioning.max_number_of_models!;
    this.form.controls.connectionMethodId.setValue(
      this.connectionMethods[0].id,
    );

    for (const model of this.data.models) {
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
      .createSession({
        tool_id: this.data.tool.id,
        version_id: this.data.toolVersion.id,
        connection_method_id: this.form.controls.connectionMethodId.value!,
        session_type: SessionType.Readonly,
        project_slug: this.data.projectSlug,
        provisioning: included.map((m) => {
          return {
            project_slug: this.data.projectSlug,
            model_slug: m.model.slug,
            git_model_id: m.primaryGitModel.id,
            revision: m.revision,
            deep_clone: m.deepClone,
          };
        }),
      })
      .subscribe({
        next: (session) => {
          this.dialog.close();
          this.router.navigate(['/session-viewer'], {
            queryParams: { 'session-id': session.id },
          });
        },
        error: () => {
          this.loading = false;
        },
      });
  }

  maxNumberOfModelsExceeded(): boolean {
    return (
      this.maxNumberOfModels !== null &&
      this.maxNumberOfModels !== undefined &&
      this.selectedModelOptions().length > this.maxNumberOfModels
    );
  }

  getSelectedConnectionMethod(): ConnectionMethod {
    return this.connectionMethods.find(
      (method) => method.id === this.form.controls.connectionMethodId.value,
    )!;
  }
}
