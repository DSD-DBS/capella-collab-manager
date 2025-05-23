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
  inject,
} from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatTabGroup, MatTab, MatTabLabel } from '@angular/material/tabs';
import { EditorComponent } from 'src/app/helpers/editor/editor.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  CreateToolVersionInput,
  Tool,
  ToolVersion,
  ToolsService,
} from 'src/app/openapi';
import { ApiDocumentationComponent } from '../../../../../general/api-documentation/api-documentation.component';
import { EditorComponent as EditorComponent_1 } from '../../../../../helpers/editor/editor.component';
import { ToolWrapperService } from '../../tool.service';

@Component({
  selector: 'app-tool-version',
  templateUrl: './tool-version.component.html',
  styleUrls: ['./tool-version.component.css'],
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
export class ToolVersionComponent {
  private toolWrapperService = inject(ToolWrapperService);
  private toastService = inject(ToastService);
  private toolsService = inject(ToolsService);

  _tool?: Tool = undefined;

  @Input()
  set tool(value: Tool | undefined) {
    if (this._tool && this._tool.id === value?.id) return;

    this._tool = value;
    this.toolVersions = undefined;

    if (this._tool !== undefined) {
      this.toolsService
        .getDefaultToolVersion(this._tool!.id)
        .subscribe((version) => {
          this.getEditorForContext('new')!.setValue(version);
        });
      this.toolsService
        .getToolVersions(this._tool.id)
        .subscribe((versions: ToolVersion[]) => {
          this.toolVersions = versions;
        });
    }
  }

  @ViewChildren('editorRef') editorRefs: QueryList<EditorComponent> | undefined;

  @ViewChild('tabGroup', { static: false }) tabGroup: MatTabGroup | undefined;

  toolVersions: ToolVersion[] | undefined = undefined;

  getEditorForContext(context: string) {
    return this.editorRefs?.find((editor) => editor.context() === context);
  }

  resetValue(context: string) {
    this.getEditorForContext(context)?.resetValue();
  }

  submitValue(context: string) {
    this.getEditorForContext(context)?.submitValue();
  }

  submittedValue(toolVersion: ToolVersion, value: ToolVersion) {
    const { id, ...valueWithoutID } = value; // eslint-disable-line @typescript-eslint/no-unused-vars
    this.toolsService
      .updateToolVersion(this._tool!.id, toolVersion.id, valueWithoutID)
      .subscribe((toolVersion: ToolVersion) => {
        this.toastService.showSuccess(
          'Tool version updated',
          `Successfully updated version '${toolVersion.name}' for tool '${this._tool!.name}'`,
        );
        const versionIdx = this.toolVersions?.findIndex(
          (v) => v.id === toolVersion.id,
        );

        this.toolVersions![versionIdx!] = toolVersion;
        this.getEditorForContext(toolVersion.id.toString())!.setValue(
          toolVersion,
        );
      });
  }

  submittedNewToolVersion(value: CreateToolVersionInput) {
    this.toolsService
      .createToolVersion(this._tool!.id, value)
      .subscribe((toolVersion: ToolVersion) => {
        this.toastService.showSuccess(
          'Tool version created',
          `Successfully created version '${toolVersion.name}' for tool '${this._tool!.name}'`,
        );
        this.toolVersions!.push(toolVersion);
        this.getEditorForContext('new')!.resetValue();
        this.jumpToLastTab();
      });
  }

  private jumpToLastTab() {
    if (!this.tabGroup || !(this.tabGroup instanceof MatTabGroup)) return;

    this.tabGroup.selectedIndex = this.tabGroup._tabs.length;
  }

  removeToolVersion(toolVersion: ToolVersion): void {
    this.toolsService
      .deleteToolVersion(this._tool!.id, toolVersion.id)
      .subscribe(() => {
        this.toolVersions = this.toolVersions!.filter(
          (version) => version.id !== toolVersion.id,
        );
      });
  }
}
