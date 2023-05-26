/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import cronstrue from 'cronstrue';
import { PluginTrigger } from 'src/app/plugins/store/service/plugin-store.service';

@Component({
  selector: 'app-pipeline-triggers',
  templateUrl: './pipeline-triggers.component.html',
  styleUrls: ['./pipeline-triggers.component.css'],
})
export class PipelineTriggersComponent {
  @Input() pipelineTrigger?: PluginTrigger = undefined;

  @Output()
  triggersFinished = new EventEmitter<any>();

  formGroup = new FormGroup({
    manual: new FormControl(true),
    cron: new FormControl(false),
  });
  // TODO: Add validator that at least one trigger is selected

  humanFriendlyCron(cron: string) {
    const uppercaseCron = cronstrue.toString(cron, { verbose: true });
    return uppercaseCron.charAt(0).toLowerCase() + uppercaseCron.slice(1);
  }

  submitTriggers() {
    this.triggersFinished.emit(this.formGroup.value);
  }
}
