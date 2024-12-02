/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Inject } from '@angular/core';
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
  constructor(
    private toolsService: ToolsService,
    public dialogRef: MatDialogRef<ToolDeletionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public tool: Tool,
  ) {}

  deleteTool(): void {
    this.toolsService.deleteTool(this.tool.id).subscribe(() => {
      this.dialogRef.close(true);
    });
  }
}
