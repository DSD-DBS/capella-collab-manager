/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ModelService } from '../projects/models/service/model.service';
import { SessionService } from '../services/session/session.service';
import {
  ToolService,
  ToolVersion,
} from '../settings/core/tools-settings/tool.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent implements OnInit {
  showSpinner = true;
  canCreateSession = true;

  versions: ToolVersion[] = [];

  public form = new FormGroup({
    toolId: new FormControl(null, Validators.required),
    versionId: new FormControl(null, Validators.required),
  });

  constructor(
    public sessionService: SessionService,
    public toolService: ToolService,
    public modelService: ModelService
  ) {}

  ngOnInit(): void {
    this.toolService.getTools().subscribe();
  }

  requestSession() {
    if (!this.form.valid) {
      return;
    }

    this.canCreateSession = false;
    this.sessionService
      .createPersistentSession(
        this.form.controls.toolId.value!,
        this.form.controls.versionId.value!
      )
      .subscribe({
        complete: () => {
          this.canCreateSession = true;
        },
      });
  }

  getVersionsForTool(toolId: number): void {
    this.versions = [];
    this.toolService
      .getVersionsForTool(toolId)
      .subscribe((res: ToolVersion[]) => {
        this.versions = res;
      });
  }
}
