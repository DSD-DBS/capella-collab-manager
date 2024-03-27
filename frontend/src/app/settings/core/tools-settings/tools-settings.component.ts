/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { combineLatest } from 'rxjs';
import {
  ToolExtended,
  ToolService,
  ToolNature,
  ToolVersion,
} from './tool.service';

@Component({
  selector: 'app-dockerimage-settings',
  templateUrl: './tools-settings.component.html',
  styleUrls: ['./tools-settings.component.css'],
})
export class ToolsSettingsComponent {
  tools: { [id: string]: ToolExtended } = {};

  constructor(public toolService: ToolService) {
    this.tools = {};
    this.toolService.getTools().subscribe(() => {
      for (const tool of this.toolService.tools!.map((tool) => tool.id)) {
        combineLatest([
          this.toolService.getNaturesForTool(tool),
          this.toolService.getVersionsForTool(tool, false),
        ]).subscribe({
          next: (result: [ToolNature[], ToolVersion[]]) => {
            this.tools[tool] = {
              natures: result[0],
              versions: result[1],
            };
          },
        });
      }
    });
  }

  mapToolVersionOrNatureToName(
    versionOrNature: ToolVersion[] | ToolNature[],
  ): string[] {
    return versionOrNature.map((elem) => elem.name);
  }
}
