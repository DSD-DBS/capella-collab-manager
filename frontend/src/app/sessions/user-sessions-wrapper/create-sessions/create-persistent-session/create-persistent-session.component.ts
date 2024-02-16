/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import {
  Session,
  SessionService,
} from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';
import {
  ConnectionMethod,
  Tool,
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';

@UntilDestroy()
@Component({
  selector: 'app-create-persistent-session',
  templateUrl: './create-persistent-session.component.html',
  styleUrls: ['./create-persistent-session.component.css'],
})
export class CreatePersistentSessionComponent implements OnInit {
  persistentSession?: Session;

  selectedTool?: Tool;
  versions: ToolVersion[] = [];

  requestInProgress = false;

  public toolSelectionForm = new FormGroup({
    toolId: new FormControl(null, Validators.required),
    versionId: new FormControl<number | null>(null, Validators.required),
    connectionMethodId: new FormControl<string | undefined>(
      undefined,
      Validators.required,
    ),
  });

  constructor(
    public toolService: ToolService,
    private sessionService: SessionService,
    private userSessionService: UserSessionService,
  ) {}

  ngOnInit(): void {
    this.toolService.getTools().subscribe();

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
      .createSession(
        this.toolSelectionForm.controls.toolId.value!,
        this.toolSelectionForm.controls.versionId.value!,
        this.toolSelectionForm.controls.connectionMethodId.value!,
        'persistent',
        [],
      )
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
    this.selectedTool = this.toolService.tools?.find(
      (tool) => tool.id == toolId,
    );
    this.toolSelectionForm.controls.connectionMethodId.setValue(
      this.selectedTool?.config.connection.methods[0].id,
    );
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
    this.toolService
      .getVersionsForTool(toolId)
      .subscribe((res: ToolVersion[]) => {
        this.versions = res;
        if (res.length) {
          this.toolSelectionForm.controls.versionId.setValue(
            (res.find((version) => version.config.is_recommended) || res[0]).id,
          );
        }
      });
  }
}
