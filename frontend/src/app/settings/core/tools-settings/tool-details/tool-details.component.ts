/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, ViewChild } from '@angular/core';

import { MatButton } from '@angular/material/button';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { ActivatedRoute, Router } from '@angular/router';
import { filter, map, mergeMap, tap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { EditorComponent } from 'src/app/helpers/editor/editor.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ApiDocumentationComponent } from '../../../../general/api-documentation/api-documentation.component';
import { EditorComponent as EditorComponent_1 } from '../../../../helpers/editor/editor.component';
import { Tool, ToolService } from '../tool.service';
import { ToolDeletionDialogComponent } from './tool-deletion-dialog/tool-deletion-dialog.component';
import { ToolNatureComponent } from './tool-nature/tool-nature.component';
import { ToolVersionComponent } from './tool-version/tool-version.component';

@Component({
  selector: 'app-tool-details',
  templateUrl: './tool-details.component.html',
  styleUrls: ['./tool-details.component.css'],
  standalone: true,
  imports: [
    ApiDocumentationComponent,
    EditorComponent_1,
    MatButton,
    MatIcon,
    ToolVersionComponent,
    ToolNatureComponent,
  ],
})
export class ToolDetailsComponent {
  @ViewChild(EditorComponent) editor: EditorComponent | undefined;

  selectedTool?: Tool;

  constructor(
    private route: ActivatedRoute,
    private toolService: ToolService,
    private toastService: ToastService,
    private breadcrumbsService: BreadcrumbsService,
    private router: Router,
    private dialog: MatDialog,
  ) {
    this.toolService.getTools().subscribe();

    this.route.params
      .pipe(
        map((params) => params.toolID),
        filter((toolID) => toolID !== undefined),
        mergeMap((toolID) => this.toolService.getToolByID(toolID)),
      )
      .subscribe({
        next: (tool) => {
          this.breadcrumbsService.updatePlaceholder({ tool });
          this.selectedTool = tool;
          this.editor!.value = this.selectedTool;
        },
      });
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  submitValue(value: any): void {
    delete value.id;
    this.toolService
      .updateTool(this.selectedTool!.id, value)
      .pipe(
        tap((tool) => {
          this.toastService.showSuccess(
            'Tool updated',
            `The configuration of the tool '${tool.name}' has been updated successfully.`,
          );
          this.editor!.value = tool;
          this.breadcrumbsService.updatePlaceholder({ tool });
        }),
      )
      .subscribe((tool) => {
        this.selectedTool = tool;
      });
  }

  deleteTool(): void {
    this.dialog
      .open(ToolDeletionDialogComponent, {
        data: this.selectedTool,
      })
      .afterClosed()
      .pipe(filter((res: boolean) => res))
      .subscribe(() => {
        this.router.navigate(['../..', 'tools'], {
          relativeTo: this.route,
        });
        this.toastService.showSuccess(
          'Tool deleted',
          `The tool '${this.selectedTool?.name}' was deleted successfully`,
        );
      });
  }
}
