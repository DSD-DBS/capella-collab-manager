/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { PluginTemplateInput } from 'src/app/plugins/store/service/plugin-store.service';

@Component({
  selector: 'app-pipeline-environment-input',
  templateUrl: './pipeline-environment-input.component.html',
  styleUrls: ['./pipeline-environment-input.component.css'],
})
export class PipelineEnvironmentInputComponent {
  form: FormGroup = new FormGroup({});

  environmentInput?: PluginTemplateEnvironmentInput = undefined;

  @Input()
  set input(input: PluginTemplateInput) {
    this.environmentInput = input as PluginTemplateEnvironmentInput;
    this.environmentInput.variables.forEach((variable) => {
      this.form.addControl(variable.key, new FormControl(variable.default));
    });
  }

  @Output()
  inputFinished = new EventEmitter<any>();

  submitInput() {
    this.inputFinished.emit(this.form.value);
  }
}

export type PluginTemplateEnvironmentInput = PluginTemplateInput & {
  variables: EnvironmentVariable[];
};

type EnvironmentVariable = {
  key: string;
  type: 'dropdown' | 'boolean';
  displayName: string;
  values: string[];
  description: string;
  default: string | boolean;
};

export type PipelineEnvironmentInput = {
  [key: string]: string;
};
