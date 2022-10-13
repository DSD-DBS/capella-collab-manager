/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Project } from 'src/app/services/project/project.service';
import { ModelService } from '../services/model/model.service';
import { DepthType, SessionService } from '../services/session/session.service';
import { ToolService, Version } from '../services/tools/tool.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent {
  repositories: Project[] = [];
  showSpinner = true;
  canCreateSession = true;

  public form = new FormGroup({
    tool_id: new FormControl(-1, Validators.required),
    version_id: new FormControl(-1, Validators.required),
  });

  constructor(
    public sessionService: SessionService,
    public toolService: ToolService,
    public modelService: ModelService
  ) {}

  ngOnInit(): void {
    this.toolService.get_tools().subscribe();
    this.toolService.get_versions().subscribe();
  }

  requestSession() {
    if (!this.form.valid) {
      return;
    }

    this.canCreateSession = false;
    this.sessionService
      .createPersistentSession(
        this.form.controls.tool_id.value,
        this.form.controls.version_id.value
      )
      .subscribe(
        (res) => {
          this.canCreateSession = true;
        },
        () => {
          this.canCreateSession = true;
        }
      );
  }

  getVersionsForTool(tool_id: number | null): Version[] {
    if (!this.toolService.versions || !tool_id) {
      return [];
    }
    return this.toolService.versions[tool_id];
  }
}
