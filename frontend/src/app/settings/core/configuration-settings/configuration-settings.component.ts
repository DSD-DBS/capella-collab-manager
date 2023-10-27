/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, HostListener, NgZone } from '@angular/core';

import * as monaco from 'monaco-editor';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ConfigurationSettingsService } from 'src/app/settings/core/configuration-settings/configuration-settings.service';
import { stringify, parse, YAMLParseError } from 'yaml';
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
    private metadataService: MetadataService,
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
      automaticLayout: true,
    });
  }

  fetchConfiguration() {
    this.configurationSettingsService
      .getConfigurationSettings('global')
      .subscribe((data) => {
        const yaml = stringify(data, { indent: 4 });
        this.intialValue = yaml;
        this.editor?.setValue(yaml);
      });
  }

  resetValue() {
    this.editor?.setValue(this.intialValue);
  }

  submitValue() {
    if (!this.editor?.getValue()) {
      this.toastService.showError(
        'Configuration is empty',
        "The configuration editor doesn't contain any content. Make sure to enter a valid YAML configuration.",
      );
      return;
    }
    let jsonValue = '';

    try {
      jsonValue = parse(this.editor?.getValue());
    } catch (e) {
      if (e instanceof YAMLParseError) {
        this.toastService.showError('YAML parsing error', e.message);
      } else {
        this.toastService.showError(
          'YAML parsing error',
          'Unknown error. Please check the console for more information.',
        );
      }
      return;
    }

    this.configurationSettingsService
      .putConfigurationSettings('global', jsonValue)
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'Configuration successfully updated',
            'The global configuration has been successfully updated. The metadata will be reloaded.',
          );
          this.fetchConfiguration();
          this.metadataService.loadBackendMetadata().subscribe();
        },
      });
  }

  @HostListener('document:keydown', ['$event'])
  saveHandler(event: KeyboardEvent) {
    if ((event.metaKey || event.ctrlKey) && event.key === 's') {
      event.preventDefault();
      event.stopPropagation();
      this.submitValue();
    }
  }
}
