/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Tool, ToolsService } from 'src/app/openapi';

@Component({
  selector: 'app-tool-deletion-dialog',
  templateUrl: './tool-deletion-dialog.component.html',
  styleUrls: ['./tool-deletion-dialog.component.css'],
  imports: [MatButton],
})
export class ToolDeletionDialogComponent {
  private toolsService = inject(ToolsService);
  dialogRef = inject<MatDialogRef<ToolDeletionDialogComponent>>(MatDialogRef);
  tool = inject<Tool>(MAT_DIALOG_DATA);

  deleteTool(): void {
    this.toolsService.deleteTool(this.tool.id).subscribe(() => {
      this.dialogRef.close(true);
    });
  }
}
