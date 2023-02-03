/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Tool, ToolService } from '../../tool.service';

@Component({
  selector: 'app-tool-deletion-dialog',
  templateUrl: './tool-deletion-dialog.component.html',
  styleUrls: ['./tool-deletion-dialog.component.css'],
})
export class ToolDeletionDialogComponent {
  constructor(
    private toolService: ToolService,
    public dialogRef: MatDialogRef<ToolDeletionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public tool: Tool
  ) {}

  deleteTool(): void {
    this.toolService.deleteTool(this.tool.id).subscribe(() => {
      this.dialogRef.close(true);
    });
  }
}
