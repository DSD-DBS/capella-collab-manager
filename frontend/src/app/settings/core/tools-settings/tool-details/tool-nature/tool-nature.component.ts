/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
import { finalize, tap } from 'rxjs';
import { Tool, ToolService, ToolNature } from '../../tool.service';

@Component({
  selector: 'app-tool-nature',
  templateUrl: './tool-nature.component.html',
  styleUrls: ['./tool-nature.component.css'],
})
export class ToolNatureComponent {
  _tool?: Tool = undefined;

  @Input()
  set tool(value: Tool | undefined) {
    if (this._tool && this._tool.id === value?.id) return;

    this._tool = value;
    this.toolNatures = [];

    this.toolService
      .getNaturesForTool(this._tool!.id)
      .subscribe((natures: ToolNature[]) => {
        this.toolNatures = natures;
      });
  }
  toolNatures: ToolNature[] = [];

  constructor(private toolService: ToolService) {}

  @ViewChild('toolNatureList') toolNatureList!: MatSelectionList;

  get selectedToolNature() {
    return this.toolNatureList.selectedOptions.selected[0].value;
  }

  toolNatureForm = new FormGroup({
    name: new FormControl('', [
      Validators.required,
      this.uniqueNameValidator(),
    ]),
  });

  uniqueNameValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      return this.toolNatures.find((nature) => nature.name == control.value)
        ? { toolVersionExists: true }
        : null;
    };
  }

  createToolNature(): void {
    if (this.toolNatureForm.valid) {
      this.toolNatureForm.disable();

      this.toolService
        .createNatureForTool(
          this._tool!.id,
          this.toolNatureForm.controls.name.value!,
        )
        .pipe(
          tap(() => {
            this.toolNatureForm.reset();
          }),
          finalize(() => {
            this.toolNatureForm.enable();
          }),
        )
        .subscribe((nature: ToolNature) => {
          this.toolNatures.push(nature);
        });
    }
  }

  removeToolNature(toolNature: ToolNature): void {
    this.toolService
      .deleteNatureForTool(this._tool!.id, toolNature)
      .subscribe(() => {
        this.toolNatures = this.toolNatures.filter(
          (nature) => nature.id !== toolNature.id,
        );
      });
  }
}
