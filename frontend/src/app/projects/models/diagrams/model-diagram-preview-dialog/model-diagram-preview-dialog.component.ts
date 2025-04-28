/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import {
  AfterViewInit,
  Component,
  ElementRef,
  ViewChild,
  inject,
} from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogClose } from '@angular/material/dialog';
import { MatDivider } from '@angular/material/divider';
import Panzoom from '@panzoom/panzoom';
import { DiagramMetadata } from 'src/app/openapi';

@Component({
  selector: 'app-model-diagram-preview-dialog',
  templateUrl: './model-diagram-preview-dialog.component.html',
  imports: [MatDivider, MatButton, MatDialogClose],
})
export class ModelDiagramPreviewDialogComponent implements AfterViewInit {
  data = inject<MatDialogPreviewData>(MAT_DIALOG_DATA);

  @ViewChild('diagram')
  diagramElement?: ElementRef;

  ngAfterViewInit(): void {
    const img = this.diagramElement!.nativeElement;

    const panzoom = Panzoom(img, {
      maxScale: 50,
    });

    img.parentElement.addEventListener('wheel', panzoom.zoomWithWheel);
  }
}

export interface MatDialogPreviewData {
  diagram: DiagramMetadata;
  content: string | ArrayBuffer;
}
