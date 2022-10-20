/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, ViewChild } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatSelectionList } from '@angular/material/list';
import { tap } from 'rxjs';
import { Tool, ToolService, ToolVersion } from '../../tool.service';

@Component({
  selector: 'app-tool-version',
  templateUrl: './tool-version.component.html',
  styleUrls: ['./tool-version.component.css'],
})
export class ToolVersionComponent {
  _tool: Tool | undefined = undefined;

  @Input()
  set tool(value: Tool | undefined) {
    this._tool = value;
    this.toolVersions = [];

    if (value) {
      this.toolService
        .getVersionsForTool(value.id)
        .subscribe((versions: ToolVersion[]) => {
          this.toolVersions = versions;
        });
    }
  }
  toolVersions: ToolVersion[] = [];

  constructor(private toolService: ToolService) {}

  @ViewChild('toolVersionList') toolVersionList!: MatSelectionList;

  get selectedToolVersion(): ToolVersion {
    return this.toolVersionList.selectedOptions.selected[0].value;
  }

  toolVersionForm = new FormGroup({
    name: new FormControl('', [
      Validators.required,
      this.uniqueNameValidator(),
    ]),
  });

  uniqueNameValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      return this.toolVersions
        .map((version) => version.name)
        .includes(control.value)
        ? { toolVersionExists: true }
        : null;
    };
  }

  createToolVersion(): void {
    if (this.toolVersionForm.valid) {
      this.toolVersionForm.disable();

      this.toolService
        .createVersionForTool(
          this._tool!.id,
          this.toolVersionForm.controls.name.value!
        )
        .pipe(
          tap({
            next: () => {
              this.toolVersionForm.reset();
            },
            complete: () => {
              this.toolVersionForm.enable();
            },
          })
        )
        .subscribe((version: ToolVersion) => {
          this.toolVersions.push(version);
        });
    }
  }

  removeToolVersion(toolVersion: ToolVersion): void {
    this.toolService
      .deleteVersionForTool(this._tool!.id, toolVersion)
      .subscribe(() => {
        this.toolVersions = this.toolVersions.filter(
          (version) => version.id !== toolVersion.id
        );
      });
  }
}
