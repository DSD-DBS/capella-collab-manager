/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatStepper } from '@angular/material/stepper';
import {
  PluginStoreService,
  Plugin,
  PluginTemplateInput,
  PluginTrigger,
} from 'src/app/plugins/store/service/plugin-store.service';
import { PipelineEnvironmentInput } from 'src/app/projects/models/backup-settings/create-pipeline/pipeline-input/pipeline-environment-input/pipeline-environment-input.component';
import { PipelineGitInput } from 'src/app/projects/models/backup-settings/create-pipeline/pipeline-input/pipeline-git-input/pipeline-git-input.component';
import { PipelineT4CInput } from 'src/app/projects/models/backup-settings/create-pipeline/pipeline-input/pipeline-t4c-input/pipeline-t4c-input.component';
import { stringify } from 'yaml';

@Component({
  selector: 'app-create-pipeline',
  templateUrl: './create-pipeline.component.html',
  styleUrls: ['./create-pipeline.component.css'],
})
export class CreatePipelineComponent {
  constructor(public pluginStoreService: PluginStoreService) {}

  selectedPlugin?: Plugin = undefined;

  requestBody: PostPipeline = {
    plugin_id: undefined,
    inputs: [],
    triggers: {},
  };

  cleanInputTypes(inputs: PluginTemplateInput[]): string[] {
    return [...new Set(inputs.map((input) => input.type))];
  }

  mapInputToDisplayName(input: string) {
    return {
      git: 'Git repository access',
      t4c: 'TeamForCapella repository access',
      yml: 'YAML configuration file',
      environment: 'Environment variables',
    }[input];
  }

  selectPlugin(stepper: MatStepper, plugin: Plugin) {
    this.requestBody['plugin_id'] = plugin.id;
    this.selectedPlugin = plugin;
    this.stepNext(stepper);
  }

  stepNext(stepper: MatStepper) {
    if (stepper.selected) stepper.selected.completed = true;
    stepper.next();
  }

  receivedInput(
    stepper: MatStepper,
    configurationStepper: MatStepper,
    inputValue: any,
  ): void {
    this.requestBody['inputs'][configurationStepper.selectedIndex] = inputValue;
    if (
      configurationStepper.selectedIndex ===
      configurationStepper.steps.length - 1
    ) {
      this.stepNext(stepper);
    } else {
      this.stepNext(configurationStepper);
    }
  }

  receivedTrigger(stepper: MatStepper, value: any): void {
    this.requestBody['triggers'] = value;

    this.stepNext(stepper);
  }

  prettifyYAML(content: any): string {
    if (content === undefined) return '';
    return stringify(content);
  }
}

type PostPipeline = {
  plugin_id?: number;
  inputs: (PipelineGitInput | PipelineT4CInput | PipelineEnvironmentInput)[];
  triggers?: PluginTrigger;
};
