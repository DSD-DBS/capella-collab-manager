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
import { finalize, tap } from 'rxjs';
import { Tool, ToolService, ToolType } from '../../tool.service';

@Component({
  selector: 'app-tool-type',
  templateUrl: './tool-type.component.html',
  styleUrls: ['./tool-type.component.css'],
})
export class ToolTypeComponent {
  _tool?: Tool = undefined;

  @Input()
  set tool(value: Tool | undefined) {
    this._tool = value;
    this.toolTypes = [];

    if (value) {
      this.toolService
        .getTypesForTool(value.id)
        .subscribe((types: ToolType[]) => {
          this.toolTypes = types;
        });
    }
  }
  toolTypes: ToolType[] = [];

  constructor(private toolService: ToolService) {}

  @ViewChild('toolTypesList') toolTypesList!: MatSelectionList;

  get selectedToolType() {
    return this.toolTypesList.selectedOptions.selected[0].value;
  }

  toolTypeForm = new FormGroup({
    name: new FormControl('', [
      Validators.required,
      this.uniqueNameValidator(),
    ]),
  });

  uniqueNameValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      return this.toolTypes.find((type) => type.name == control.value)
        ? { toolVersionExists: true }
        : null;
    };
  }

  createToolType(): void {
    if (this.toolTypeForm.valid) {
      this.toolTypeForm.disable();

      this.toolService
        .createTypeForTool(
          this._tool!.id,
          this.toolTypeForm.controls.name.value!
        )
        .pipe(
          tap(() => {
            this.toolTypeForm.reset();
          }),
          finalize(() => {
            this.toolTypeForm.enable();
          })
        )
        .subscribe((type: ToolType) => {
          this.toolTypes.push(type);
        });
    }
  }

  removeToolType(toolType: ToolType): void {
    this.toolService
      .deleteTypeForTool(this._tool!.id, toolType)
      .subscribe(() => {
        this.toolTypes = this.toolTypes.filter(
          (type) => type.id !== toolType.id
        );
      });
  }
}
