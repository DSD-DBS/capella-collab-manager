/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  Component,
  Input,
  QueryList,
  ViewChild,
  ViewChildren,
} from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatTabGroup, MatTab, MatTabLabel } from '@angular/material/tabs';
import { EditorComponent } from 'src/app/helpers/editor/editor.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  CreateToolNatureInput,
  Tool,
  ToolNature,
  ToolsService,
} from 'src/app/openapi';
import { ApiDocumentationComponent } from '../../../../../general/api-documentation/api-documentation.component';
import { EditorComponent as EditorComponent_1 } from '../../../../../helpers/editor/editor.component';

@Component({
  selector: 'app-tool-nature',
  templateUrl: './tool-nature.component.html',
  styleUrls: ['./tool-nature.component.css'],
  imports: [
    ApiDocumentationComponent,
    MatTabGroup,
    MatTab,
    MatTabLabel,
    MatIcon,
    EditorComponent_1,
    MatButton,
  ],
})
export class ToolNatureComponent {
  _tool?: Tool = undefined;

  @Input()
  set tool(value: Tool | undefined) {
    if (this._tool && this._tool.id === value?.id) return;

    this._tool = value;
    this.toolNatures = undefined;

    if (this._tool !== undefined) {
      this.toolsService
        .getDefaultToolNature(this._tool!.id)
        .subscribe((nature) => {
          this.getEditorForContext('new')!.setValue(nature);
        });
      this.toolsService
        .getToolNatures(this._tool.id)
        .subscribe((natures: ToolNature[]) => {
          this.toolNatures = natures;
        });
    }
  }

  @ViewChildren('editorRef') editorRefs: QueryList<EditorComponent> | undefined;

  @ViewChild('tabGroup', { static: false }) tabGroup: MatTabGroup | undefined;

  toolNatures: ToolNature[] | undefined = undefined;

  constructor(
    private toastService: ToastService,
    private toolsService: ToolsService,
  ) {}

  getEditorForContext(context: string) {
    return this.editorRefs?.find((editor) => editor.context() === context);
  }

  resetValue(context: string) {
    this.getEditorForContext(context)?.resetValue();
  }

  submitValue(context: string) {
    this.getEditorForContext(context)?.submitValue();
  }

  submittedValue(toolNature: ToolNature, value: ToolNature) {
    const { id, ...valueWithoutID } = value; // eslint-disable-line @typescript-eslint/no-unused-vars
    this.toolsService
      .updateToolNature(this._tool!.id, toolNature.id, valueWithoutID)
      .subscribe((toolNature: ToolNature) => {
        this.toastService.showSuccess(
          'Tool nature updated',
          `Successfully updated nature '${toolNature.name}' for tool '${this._tool!.name}'`,
        );
        const natureIdx = this.toolNatures?.findIndex(
          (v) => v.id === toolNature.id,
        );

        this.toolNatures![natureIdx!] = toolNature;
        this.getEditorForContext(toolNature.id.toString())!.setValue(
          toolNature,
        );
      });
  }

  submittedNewToolNature(value: CreateToolNatureInput) {
    this.toolsService
      .createToolNature(this._tool!.id, value)
      .subscribe((toolNature: ToolNature) => {
        this.toastService.showSuccess(
          'Tool nature created',
          `Successfully created nature '${toolNature.name}' for tool '${this._tool!.name}'`,
        );
        this.toolNatures!.push(toolNature);
        this.getEditorForContext('new')!.resetValue();
        this.jumpToLastTab();
      });
  }

  private jumpToLastTab() {
    if (!this.tabGroup || !(this.tabGroup instanceof MatTabGroup)) return;

    this.tabGroup.selectedIndex = this.tabGroup._tabs.length;
  }

  removeToolNature(toolNature: ToolNature): void {
    this.toolsService
      .deleteToolNature(this._tool!.id, toolNature.id)
      .subscribe(() => {
        this.toolNatures = this.toolNatures!.filter(
          (nature) => nature.id !== toolNature.id,
        );
      });
  }
}
