/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  Component,
  computed,
  effect,
  ElementRef,
  EventEmitter,
  HostListener,
  input,
  model,
  Output,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { type editor } from 'monaco-editor';
import { MonacoEditorModule, NgxEditorModel } from 'ngx-monaco-editor-v2';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { v4 as uuidv4 } from 'uuid';
import { URI } from 'vscode-uri';
import { stringify, parse, YAMLParseError } from 'yaml';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  standalone: true,
  imports: [MonacoEditorModule, FormsModule],
})
export class EditorComponent {
  height = input('400px');
  lineWidth = input(55);
  // Helps to identify the editor in the DOM
  context = input(uuidv4());
  value = input<unknown>();
  editor = signal<editor.IStandaloneCodeEditor | null>(null);

  type = input<'globalconfig' | 'tool' | 'toolnature' | 'toolversion'>();

  initialValue = signal('Loading...');
  code = model(this.initialValue());

  options: editor.IStandaloneEditorConstructionOptions = {
    language: 'yaml',
    minimap: { enabled: false },
    overviewRulerBorder: false,
    scrollBeyondLastLine: false,
    automaticLayout: true,
    tabSize: 2,
    fixedOverflowWidgets: true,
  };

  editorModel = computed<NgxEditorModel>(() => ({
    value: this.initialValue(),
    language: 'yaml',
    uri: URI.parse(`file:///${this.context()}.${this.type()}.yaml`),
  }));

  @Output()
  submitted = new EventEmitter();

  constructor(
    private toastService: ToastService,
    private el: ElementRef,
  ) {
    effect(() => {
      this.setValue(this.value());
    });
  }

  onInit(editor: editor.IStandaloneCodeEditor) {
    this.editor.set(editor);
  }

  public setValue(data: unknown) {
    if (!data) return;
    const yaml = stringify(data, { indent: 2, lineWidth: this.lineWidth() });
    if (this.initialValue() === 'Loading...') {
      this.initialValue.set(yaml);
    }
    this.code.set(yaml);
    this.editor()?.setValue(yaml);
  }

  resetValue() {
    this.code.set(this.initialValue());
    this.editor()?.setValue(this.initialValue());
  }

  submitValue() {
    const editorValue = this.code();

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
