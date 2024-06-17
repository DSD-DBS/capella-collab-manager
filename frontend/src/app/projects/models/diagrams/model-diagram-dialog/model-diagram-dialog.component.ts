/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { DatePipe } from '@angular/common';
import {
  Component,
  Inject,
  ViewChildren,
  ElementRef,
  QueryList,
  OnInit,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import {
  MatDialog,
  MAT_DIALOG_DATA,
  MatDialogRef,
  MatDialogClose,
} from '@angular/material/dialog';
import { MatDivider } from '@angular/material/divider';
import {
  MatFormField,
  MatLabel,
  MatSuffix,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatTooltip } from '@angular/material/tooltip';
import { saveAs } from 'file-saver';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import {
  DiagramCacheMetadata,
  DiagramMetadata,
  Project,
  ProjectsModelsDiagramsService,
  ToolModel,
} from 'src/app/openapi';
import {
  MatDialogPreviewData,
  ModelDiagramPreviewDialogComponent,
} from 'src/app/projects/models/diagrams/model-diagram-preview-dialog/model-diagram-preview-dialog.component';
import { ModelDiagramCodeBlockComponent } from './model-diagram-code-block/model-diagram-code-block.component';

@Component({
  selector: 'app-model-diagram-dialog',
  templateUrl: './model-diagram-dialog.component.html',
  styleUrls: ['./model-diagram-dialog.component.css'],
  standalone: true,
  imports: [
    ModelDiagramCodeBlockComponent,
    MatFormField,
    MatLabel,
    MatInput,
    FormsModule,
    MatIcon,
    MatSuffix,
    MatTooltip,
    NgxSkeletonLoaderModule,
    MatButton,
    MatDivider,
    MatDialogClose,
    DatePipe,
  ],
})
export class ModelDiagramDialogComponent implements OnInit {
  diagramMetadata?: DiagramCacheMetadata;
  diagrams: Diagrams = {};

  loaderArray = Array(60).fill(0);

  @ViewChildren('diagram', { read: ElementRef })
  diagramHTMLElements?: QueryList<ElementRef>;

  search = '';

  get filteredDiagrams(): DiagramMetadata[] | undefined {
    if (!this.diagramMetadata) {
      return undefined;
    }

    return this.diagramMetadata.diagrams.filter(
      (diagram: DiagramMetadata) =>
        diagram.name.toLowerCase().includes(this.search.toLowerCase()) ||
        diagram.uuid.toLowerCase().includes(this.search.toLowerCase()),
    );
  }

  constructor(
    private dialog: MatDialog,
    private dialogRef: MatDialogRef<ModelDiagramDialogComponent>,
    private projectsModelsDiagramsService: ProjectsModelsDiagramsService,
    @Inject(MAT_DIALOG_DATA)
    public data: { model: ToolModel; project: Project },
  ) {}

  ngOnInit(): void {
    this.projectsModelsDiagramsService
      .getDiagramMetadata(this.data.project.slug, this.data.model.slug)
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
      },
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
      this.projectsModelsDiagramsService
        .getDiagram(uuid, this.data.project.slug, this.data.model.slug)
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
        maxWidth: '100vw',
        panelClass: [
          'md:w-[85vw]',
          'md:h-[85vw]',
          'md:max-h-[85vh]',
          'max-h-full',
          'w-full',
          'h-full',
          '!max-w-full',
        ],
        data: {
          diagram: diagram,
          content: loadingDiagram.content,
        } as MatDialogPreviewData,
      });
    }
  }

  downloadDiagram(uuid: string) {
    this.projectsModelsDiagramsService
      .getDiagram(uuid, this.data.project.slug, this.data.model.slug)
      .subscribe((response: Blob) => {
        saveAs(response, `${uuid}.svg`);
      });
  }
}

export interface Diagrams {
  [uuid: string]: Diagram;
}

type Diagram = {
  loading: boolean;
  content?: string | ArrayBuffer | null;
};
