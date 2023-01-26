/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { saveAs } from 'file-saver';
import {
  DiagramCacheMetadata,
  DiagramMetadata,
  ModelDiagramService,
} from 'src/app/projects/models/diagrams/service/model-diagram.service';
import { Model } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-model-diagram-dialog',
  templateUrl: './model-diagram-dialog.component.html',
  styleUrls: ['./model-diagram-dialog.component.css'],
})
export class ModelDiagramDialogComponent {
  diagramMetadata?: DiagramCacheMetadata = undefined;
  selectedDiagram?: DiagramMetadata = undefined;
  selectedDiagramContent?: string = undefined;

  search = '';

  filteredDiagrams() {
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
    private projectService: ProjectService,
    @Inject(MAT_DIALOG_DATA) public data: { model: Model }
  ) {
    this.modelDiagramService
      .loadDiagramMetadata(
        this.projectService.project!.slug,
        this.data.model.slug
      )
      .subscribe((diagramMetadata) => (this.diagramMetadata = diagramMetadata));
  }

  downloadDiagram(uuid: string) {
    this.modelDiagramService
      .loadDiagram(
        this.projectService.project!.slug,
        this.data.model.slug,
        uuid
      )
      .subscribe((response: Blob) => {
        saveAs(response, `${uuid}.svg`);
      });
  }
}
