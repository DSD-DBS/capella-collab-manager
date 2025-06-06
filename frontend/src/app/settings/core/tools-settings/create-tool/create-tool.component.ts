/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, ViewChild, inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { ActivatedRoute, Router } from '@angular/router';
import { EditorComponent } from 'src/app/helpers/editor/editor.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { CreateToolInput, ToolsService } from 'src/app/openapi';
import { EditorComponent as EditorComponent_1 } from '../../../../helpers/editor/editor.component';

@Component({
  selector: 'app-create-tool',
  templateUrl: './create-tool.component.html',
  imports: [EditorComponent_1, MatButton, MatIcon],
})
export class CreateToolComponent {
  private toolsService = inject(ToolsService);
  private toastService = inject(ToastService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  @ViewChild(EditorComponent) editor: EditorComponent | undefined;

  constructor() {
    this.toolsService.getDefaultTool().subscribe((tool) => {
      this.editor!.setValue(tool);
    });
  }

  submitValue(value: CreateToolInput): void {
    this.toolsService.createTool(value).subscribe((tool) => {
      this.toastService.showSuccess(
        'Tool created',
        `The tool with the name '${tool.name}' has been created successfully.`,
      );
      this.router.navigate(['../../tool', tool.id], { relativeTo: this.route });
    });
  }
}
