/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, NgZone } from '@angular/core';

import * as monaco from 'monaco-editor';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ConfigurationSettingsService } from 'src/app/settings/core/configuration-settings/configuration-settings.service';
import { stringify, parse } from 'yaml';
@Component({
  selector: 'app-configuration-settings',
  templateUrl: './configuration-settings.component.html',
})
export class ConfigurationSettingsComponent {
  private editor?: monaco.editor.IStandaloneCodeEditor = undefined;

  intialValue = 'Loading...';

  constructor(
    private ngZone: NgZone,
    private configurationSettingsService: ConfigurationSettingsService,
    private toastService: ToastService,
  ) {}

  ngOnInit() {
    this.ngZone.runOutsideAngular(() => {
      this.initMonaco();
    });

    this.fetchConfiguration();
  }

  ngOnDestroy() {
    if (this.editor) {
      this.editor.dispose();
    }
  }

  private initMonaco() {
    const configModel = monaco.editor.createModel(this.intialValue, 'yaml');

    this.editor = monaco.editor.create(document.getElementById('editor')!, {
      value: 'Loading...',
      language: 'yaml',
      scrollBeyondLastLine: false,
      model: configModel,
    });
  }

  fetchConfiguration() {
    this.configurationSettingsService
      .getConfigurationSettings('global')
      .subscribe((data) => {
        const yaml = stringify(data);
        this.intialValue = yaml;
        this.editor?.setValue(yaml);
      });
  }

  resetValue() {
    this.editor?.setValue(this.intialValue);
  }

  submitValue() {
    if (!this.editor?.getValue()) {
      return;
    }
    const jsonValue = parse(this.editor?.getValue());
    this.configurationSettingsService
      .putConfigurationSettings('global', jsonValue)
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'Global configuration successfully updated',
            '',
          );
          this.fetchConfiguration();
        },
      });
  }
}
