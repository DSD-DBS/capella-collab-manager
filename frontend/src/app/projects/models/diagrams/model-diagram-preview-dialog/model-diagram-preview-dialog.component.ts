/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DiagramMetadata } from 'src/app/projects/models/diagrams/service/model-diagram.service';

@Component({
  selector: 'app-model-diagram-preview-dialog',
  templateUrl: './model-diagram-preview-dialog.component.html',
  styleUrls: ['./model-diagram-preview-dialog.component.css'],
})
export class ModelDiagramPreviewDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA)
    public data: MatDialogPreviewData
  ) {}
}

export type MatDialogPreviewData = {
  diagram: DiagramMetadata;
  content: string | ArrayBuffer;
};
