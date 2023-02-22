/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { saveAs } from 'file-saver';
import {
  DiagramCacheMetadata,
  DiagramMetadata,
  ModelDiagramService,
} from 'src/app/projects/models/diagrams/service/model-diagram.service';

@Component({
  selector: 'app-model-diagram-dialog',
  templateUrl: './model-diagram-dialog.component.html',
  styleUrls: ['./model-diagram-dialog.component.css'],
})
export class ModelDiagramDialogComponent {
  diagramMetadata?: DiagramCacheMetadata;
  selectedDiagram?: DiagramMetadata;
  selectedDiagramContent?: string;

  search = '';

  filteredDiagrams(): DiagramMetadata[] | undefined {
    if (!this.diagramMetadata) {
      return undefined;
    }
    return this.diagramMetadata.diagrams.filter(
      (diagram: DiagramMetadata) =>
        diagram.name.toLowerCase().includes(this.search.toLowerCase()) ||
        diagram.uuid.toLowerCase().includes(this.search.toLowerCase())
    );
  }

  constructor(
    private modelDiagramService: ModelDiagramService,
    private dialogRef: MatDialogRef<ModelDiagramDialogComponent>,
    @Inject(MAT_DIALOG_DATA)
    public data: { modelSlug: string; projectSlug: string }
  ) {
    this.modelDiagramService
      .getDiagramMetadata(this.data.projectSlug, this.data.modelSlug)
      .subscribe({
        next: (diagramMetadata) => {
          this.diagramMetadata = diagramMetadata;
        },
        error: () => {
          this.dialogRef.close();
        },
      });
  }

  downloadDiagram(uuid: string) {
    this.modelDiagramService
      .getDiagram(this.data.projectSlug, this.data.modelSlug, uuid)
      .subscribe((response: Blob) => {
        saveAs(response, `${uuid}.svg`);
      });
  }
}
