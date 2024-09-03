/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgFor, NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { MatRipple } from '@angular/material/core';
import { MatIcon } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { combineLatest } from 'rxjs';
import { ToolNature, ToolVersion } from 'src/app/openapi';
import { MatIconComponent } from '../../../helpers/mat-icon/mat-icon.component';
import { ToolExtended, ToolWrapperService } from './tool.service';

@Component({
  selector: 'app-dockerimage-settings',
  templateUrl: './tools-settings.component.html',
  styleUrls: ['./tools-settings.component.css'],
  standalone: true,
  imports: [RouterLink, MatRipple, MatIconComponent, NgFor, NgIf, MatIcon],
})
export class ToolsSettingsComponent {
  tools: Record<string, ToolExtended> = {};

  constructor(public toolService: ToolWrapperService) {
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
