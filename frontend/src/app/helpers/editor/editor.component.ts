/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  EventEmitter,
  HostListener,
  Input,
  NgZone,
  Output,
} from '@angular/core';

import * as monaco from 'monaco-editor';
import { MetadataService } from 'src/app/general/metadata/metadata.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ConfigurationSettingsService } from 'src/app/settings/core/configuration-settings/configuration-settings.service';
import { stringify, parse, YAMLParseError } from 'yaml';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
})
export class EditorComponent {
  private editor?: monaco.editor.IStandaloneCodeEditor = undefined;
  intialValue = 'Loading...';

  @Output()
  submitted = new EventEmitter();

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
  }

  @Input()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  set value(data: any) {
    const yaml = stringify(data, { indent: 4 });
    this.intialValue = yaml;
    this.editor?.setValue(yaml);
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

    this.submitted.emit(jsonValue);
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

  @HostListener('document:keydown', ['$event'])
  saveHandler(event: KeyboardEvent) {
    if ((event.metaKey || event.ctrlKey) && event.key === 's') {
      event.preventDefault();
      event.stopPropagation();
      this.submitValue();
    }
  }
}
