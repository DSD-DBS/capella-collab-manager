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
import { ModelService } from 'src/app/projects/models/service/model.service';
import { UserService } from 'src/app/services/user/user.service';
import { TokenService } from 'src/app/users/basic-auth-service/basic-auth-token.service';

@Component({
  selector: 'app-model-diagram-dialog',
  templateUrl: './model-diagram-dialog.component.html',
  styleUrls: ['./model-diagram-dialog.component.css'],
})
export class ModelDiagramDialogComponent {
  diagramMetadata?: DiagramCacheMetadata;
  diagrams: Diagrams = {};
  username?: string;
  passwordValue?: string;
  path?: string;

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
        diagram.uuid.toLowerCase().includes(this.search.toLowerCase()),
    );
  }

  constructor(
    private modelDiagramService: ModelDiagramService,
    private userService: UserService,
    private modelService: ModelService,
    private tokenService: TokenService,
    private dialogRef: MatDialogRef<ModelDiagramDialogComponent>,
    private dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA)
    public data: { modelSlug: string; projectSlug: string },
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

    this.userService
      .getCurrentUser()
      .subscribe((user) => (this.username = user.name));
    this.path = this.modelService.backendURLFactory(
      data.projectSlug,
      data.modelSlug,
    );
  }

  get codeBlockContent(): string {
    return `model = capellambse.MelodyModel(
      path="path to the aird file of the model on your machine",
      diagram_cache={
        "path": "http://localhost:8000/api/v1/projects/coffee-machine/models/coffee-machine/diagrams/%s",
        "username": "${this.username}",
        "password": "${
          this.passwordValue ? this.passwordValue : 'yourPassword'
        }",
      }
    )`;
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
    this.modelDiagramService
      .getDiagram(this.data.projectSlug, this.data.modelSlug, uuid)
      .subscribe((response: Blob) => {
        saveAs(response, `${uuid}.svg`);
      });
  }

  async insertToken() {
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() + 30);
    this.tokenService
      .createToken(
        'Created in diagram cache dialog',
        expirationDate,
        'Diagram-cache',
      )
      .subscribe((token) => (this.passwordValue = token.password));
  }
}

interface Diagrams {
  [uuid: string]: Diagram;
}

type Diagram = {
  loading: boolean;
  content?: string | ArrayBuffer | null;
};
