/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  AfterViewInit,
  Component,
  ElementRef,
  Inject,
  ViewChild,
} from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import Panzoom from '@panzoom/panzoom';
import { DiagramMetadata } from 'src/app/projects/models/diagrams/service/model-diagram.service';

@Component({
  selector: 'app-model-diagram-preview-dialog',
  templateUrl: './model-diagram-preview-dialog.component.html',
  styleUrls: ['./model-diagram-preview-dialog.component.css'],
})
export class ModelDiagramPreviewDialogComponent implements AfterViewInit {
  @ViewChild('diagram')
  diagramElement?: ElementRef;

  constructor(
    @Inject(MAT_DIALOG_DATA)
    public data: MatDialogPreviewData,
  ) {}

  ngAfterViewInit(): void {
    const img = this.diagramElement!.nativeElement;

    const panzoom = Panzoom(img, {
      maxScale: 50,
    });

    img.parentElement.addEventListener('wheel', panzoom.zoomWithWheel);
  }
}

export type MatDialogPreviewData = {
  diagram: DiagramMetadata;
  content: string | ArrayBuffer;
};
