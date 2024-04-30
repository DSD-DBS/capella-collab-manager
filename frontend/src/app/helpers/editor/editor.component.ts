/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  NgZone,
  Output,
  ViewChild,
} from '@angular/core';

import * as monaco from 'monaco-editor';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { v4 as uuidv4 } from 'uuid';
import { stringify, parse, YAMLParseError } from 'yaml';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  standalone: true,
})
export class EditorComponent implements AfterViewInit {
  @Input()
  height = '400px';

  @Input()
  lineWidth = 55;

  @Input()
  // Helps to identify the editor in the DOM
  context = uuidv4();

  private editor?: monaco.editor.IStandaloneCodeEditor = undefined;
  intialValue = 'Loading...';

  @ViewChild('editorRef') editorRef: ElementRef | undefined;

  @Output()
  submitted = new EventEmitter();

  constructor(
    private ngZone: NgZone,
    private toastService: ToastService,
    private el: ElementRef,
  ) {}

  ngAfterViewInit(): void {
    this.ngZone.runOutsideAngular(() => {
      this.initMonaco();
    });
  }

  @Input()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  set value(data: any) {
    const yaml = stringify(data, { indent: 2, lineWidth: this.lineWidth });
    this.intialValue = yaml;
    this.editor?.setValue(yaml);
  }

  resetValue() {
    this.editor?.setValue(this.intialValue);
  }

  submitValue() {
    const editorValue = this.editor?.getValue();

    if (!editorValue) {
      this.toastService.showError(
        'Configuration is empty',
        "The configuration editor doesn't contain any content. Make sure to enter a valid YAML configuration.",
      );
      return;
    }

    if (editorValue === 'Loading...') {
      this.toastService.showError(
        'Configuration is still loading',
        'The configuration editor is still loading. Please wait a moment.',
      );
      return;
    }

    let jsonValue = '';

    try {
      jsonValue = parse(editorValue);
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

    this.editor = monaco.editor.create(this.editorRef?.nativeElement, {
      value: 'Loading...',
      language: 'yaml',
      minimap: { enabled: false },
      overviewRulerBorder: false,
      scrollBeyondLastLine: false,
      model: configModel,
      automaticLayout: true,
      tabSize: 2,
    });
  }

  @HostListener('document:keydown', ['$event'])
  saveHandler(event: KeyboardEvent) {
    if (this.el.nativeElement.contains(event.target)) {
      if ((event.metaKey || event.ctrlKey) && event.key === 's') {
        event.preventDefault();
        event.stopPropagation();
        this.submitValue();
      }
    }
  }
}
