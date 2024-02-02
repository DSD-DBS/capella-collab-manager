/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { MatSelectionListChange } from '@angular/material/list';
import { finalize, switchMap, tap } from 'rxjs';
import {
  PatchToolVersion,
  Tool,
  ToolService,
  ToolVersion,
} from '../../tool.service';

@Component({
  selector: 'app-tool-version',
  templateUrl: './tool-version.component.html',
  styleUrls: ['./tool-version.component.css'],
})
export class ToolVersionComponent implements OnInit {
  _tool?: Tool = undefined;

  @Input()
  set tool(value: Tool | undefined) {
    if (this._tool && this._tool.id === value?.id) return;

    this._tool = value;
    this.toolVersions = [];

    this.toolService
      .getVersionsForTool(this._tool!.id)
      .subscribe((versions: ToolVersion[]) => {
        this.toolVersions = versions;
      });
  }

  toolVersions: ToolVersion[] = [];

  constructor(private toolService: ToolService) {}

  loadingMetadata = false;
  toolVersionForm = new FormGroup({
    name: new FormControl('', [
      Validators.required,
      this.uniqueNameValidator(),
    ]),
  });

  toolVersionMetadataForm = new FormGroup({
    isDeprecated: new FormControl(false),
    isRecommended: new FormControl(false),
  });

  selectedToolVersion: ToolVersion | undefined = undefined;

  isToolVersionSelected(toolVersion: ToolVersion) {
    return toolVersion.id === this.selectedToolVersion?.id;
  }

  onSelectionChange(event: MatSelectionListChange) {
    this.selectedToolVersion = event.options[0].value;
    this.toolVersionMetadataForm.patchValue({
      isDeprecated: this.selectedToolVersion?.is_deprecated,
      isRecommended: this.selectedToolVersion?.is_recommended,
    });
  }

  ngOnInit(): void {
    this.onToolVersionMetadataFormChanges();
  }

  onToolVersionMetadataFormChanges(): void {
    this.toolVersionMetadataForm.valueChanges
      .pipe(
        tap(() => {
          this.loadingMetadata = true;
        }),
        switchMap(() => {
          return this.toolService.patchToolVersion(
            this._tool!.id,
            this.selectedToolVersion!.id,
            this.toolVersionMetadataForm.value as PatchToolVersion,
          );
        }),
        tap(() => {
          this.loadingMetadata = false;
        }),
      )
      .subscribe((res) => {
        const index = this.toolVersions.findIndex(
          (version) => version.id === res.id,
        );
        this.toolVersions[index] = res;
        this.selectedToolVersion = res;
      });
  }

  uniqueNameValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      return this.toolVersions.find((version) => version.name == control.value)
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
          this.toolVersionForm.controls.name.value!,
        )
        .pipe(
          tap(() => {
            this.toolVersionForm.reset();
          }),
          finalize(() => {
            this.toolVersionForm.enable();
          }),
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
          (version) => version.id !== toolVersion.id,
        );
      });
  }
}
