/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  Inject,
  ViewChildren,
  ElementRef,
  QueryList,
} from '@angular/core';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';
import { saveAs } from 'file-saver';
import {
  MatDialogPreviewData,
  ModelDiagramPreviewDialogComponent,
} from 'src/app/projects/models/diagrams/model-diagram-preview-dialog/model-diagram-preview-dialog.component';
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
  diagrams: Diagrams = {};

  loaderArray = Array(60).fill(0);

  @ViewChildren('diagram', { read: ElementRef })
  diagramHTMLElements?: QueryList<ElementRef>;

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
    private dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA)
    public data: { modelSlug: string; projectSlug: string; path: string }
  ) {
    this.modelDiagramService
      .getDiagramMetadata(this.data.projectSlug, this.data.modelSlug)
      .subscribe({
        next: (diagramMetadata) => {
          this.diagramMetadata = diagramMetadata;
          this.observeVisibleDiagrams();
        },
        error: () => {
          this.dialogRef.close();
        },
      });
  }

  observeVisibleDiagrams() {
    const observer = new IntersectionObserver(
      (entries: IntersectionObserverEntry[], _: IntersectionObserver) => {
        entries
          .filter((entry) => entry.isIntersecting)
          .filter((entry) => {
            return entry.target.getAttribute('success') === 'true';
          })
          .forEach((entry) => {
            const uuid = entry.target.id;
            this.lazyLoadDiagram(uuid);
          });
      },
      {
        root: null,
        threshold: 0.2,
      }
    );

    this.diagramHTMLElements?.changes.subscribe((res) => {
      res.forEach((diagram: ElementRef) => {
        observer.observe(diagram.nativeElement);
      });
    });
  }

  lazyLoadDiagram(uuid: string) {
    if (!this.diagrams[uuid]) {
      this.diagrams[uuid] = { loading: true, content: undefined };
      this.modelDiagramService
        .getDiagram(this.data.projectSlug, this.data.modelSlug, uuid)
        .subscribe({
          next: (response: Blob) => {
            const reader = new FileReader();
            reader.readAsDataURL(response);
            reader.onloadend = () => {
              const base64data = reader.result;
              this.diagrams[uuid] = {
                loading: false,
                content: base64data,
              };
            };
          },
          error: () => {
            this.diagrams[uuid] = {
              loading: false,
              content: null,
            };
          },
        });
    }
  }

  openModelDiagramPreviewDialog(diagram: DiagramMetadata) {
    const loadingDiagram = this.diagrams[diagram.uuid];
    if (!loadingDiagram.loading) {
      this.dialog.open(ModelDiagramPreviewDialogComponent, {
        height: '80vh',
        width: '80vw',
        data: {
          diagram: diagram,
          content: loadingDiagram.content,
        } as MatDialogPreviewData,
      });
    }
  }

  downloadDiagram(uuid: string) {
    this.modelDiagramService
      .getDiagram(this.data.projectSlug, this.data.modelSlug, uuid)
      .subscribe((response: Blob) => {
        saveAs(response, `${uuid}.svg`);
      });
  }
}

interface Diagrams {
  [uuid: string]: Diagram;
}

type Diagram = {
  loading: boolean;
  content?: string | ArrayBuffer | null;
};
