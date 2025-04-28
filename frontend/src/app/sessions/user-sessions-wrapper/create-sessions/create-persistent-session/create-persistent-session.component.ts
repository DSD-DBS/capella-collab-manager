/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatError, MatFormField, MatLabel } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatRadioButton, MatRadioGroup } from '@angular/material/radio';
import { MatSelect } from '@angular/material/select';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { map, Observable } from 'rxjs';
import {
  Session,
  SessionType,
  Tool,
  ToolsService,
  ToolVersion,
} from 'src/app/openapi';
import { SessionService } from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';
import {
  ConnectionMethod,
  ToolWrapperService,
} from 'src/app/settings/core/tools-settings/tool.service';
import { LicenseIndicatorComponent } from '../../../license-indicator/license-indicator.component';
import { CreateSessionHistoryComponent } from '../create-session-history/create-session-history.component';

@UntilDestroy()
@Component({
  selector: 'app-create-persistent-session',
  templateUrl: './create-persistent-session.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatError,
    MatRadioGroup,
    MatRadioButton,
    MatButton,
    MatIcon,
    CreateSessionHistoryComponent,
    AsyncPipe,
    LicenseIndicatorComponent,
  ],
})
export class CreatePersistentSessionComponent implements OnInit {
  private toolWrapperService = inject(ToolWrapperService);
  private sessionService = inject(SessionService);
  private userSessionService = inject(UserSessionService);
  private toolsService = inject(ToolsService);

  persistentSession?: Session;

  selectedTool?: Tool;
  versions: ToolVersion[] = [];

  requestInProgress = false;

  public toolSelectionForm = new FormGroup({
    toolId: new FormControl<number | null>(null, Validators.required),
    versionId: new FormControl<number | null>(
      { value: null, disabled: true },
      Validators.required,
    ),
    connectionMethodId: new FormControl<string | undefined>(
      undefined,
      Validators.required,
    ),
  });

  ngOnInit(): void {
    this.toolWrapperService.getTools().subscribe();

    this.userSessionService.persistentSessions$
      .pipe(untilDestroyed(this))
      .subscribe((sessions) => (this.persistentSession = sessions?.at(0)));
  }

  requestPersistentSession() {
    if (!this.toolSelectionForm.valid && !this.persistentSession) {
      return;
    }

    this.requestInProgress = true;

    this.sessionService
      .createSession({
        tool_id: this.toolSelectionForm.controls.toolId.value!,
        version_id: this.toolSelectionForm.controls.versionId.value!,
        connection_method_id:
          this.toolSelectionForm.controls.connectionMethodId.value!,
        session_type: SessionType.Persistent,
      })
      .subscribe({
        next: () => {
          this.userSessionService.loadSessions();
          this.requestInProgress = false;
        },
        error: () => {
          this.requestInProgress = false;
        },
      });
  }

  toolSelectionChange(toolId: number) {
    this.getVersionsForTool(toolId);
    this.selectedTool = this.toolWrapperService.tools?.find(
      (tool) => tool.id == toolId,
    );
    this.toolSelectionForm.controls.connectionMethodId.setValue(
      this.selectedTool?.config.connection.methods[0].id,
    );
    this.toolSelectionForm.controls.versionId.enable();
  }

  getSelectedConnectionMethod(): ConnectionMethod | undefined {
    if (!this.selectedTool) return undefined;
    return this.selectedTool.config.connection.methods.find(
      (method) =>
        method.id === this.toolSelectionForm.controls.connectionMethodId.value,
    )!;
  }

  getVersionsForTool(toolId: number): void {
    this.versions = [];
    this.toolsService
      .getToolVersions(toolId)
      .subscribe((res: ToolVersion[]) => {
        this.versions = res;
        if (res.length) {
          this.toolSelectionForm.controls.versionId.setValue(
            (res.find((version) => version.config.is_recommended) || res[0]).id,
          );
        }
      });
  }

  get toolsWithWorkspaceEnabled(): Observable<Tool[] | undefined> {
    return this.toolWrapperService.tools$.pipe(
      map((tools) =>
        tools?.filter(
          (tool) =>
            tool.config.persistent_workspaces.mounting_enabled &&
            !tool.config.provisioning.required,
        ),
      ),
    );
  }
}
