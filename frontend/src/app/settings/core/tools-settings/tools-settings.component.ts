/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { combineLatest } from 'rxjs';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
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

  constructor(
    private navbarService: NavBarService,
    public toolService: ToolService
  ) {
    this.navbarService.title = 'Settings / Core / Tools';
    this.tools = {};
    this.toolService.getTools().subscribe(() => {
      for (let tool of this.toolService.tools!.map((tool) => tool.id)) {
        combineLatest([
          this.toolService.getNaturesForTool(tool),
          this.toolService.getVersionsForTool(tool),
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

  mapToolVersionOrTypeToName(
    versionOrType: ToolVersion[] | ToolNature[]
  ): string[] {
    return versionOrType.map((elem) => elem.name);
  }
}
