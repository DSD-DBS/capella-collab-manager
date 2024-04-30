/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  CdkDragDrop,
  moveItemInArray,
  CdkDropList,
  CdkDrag,
} from '@angular/cdk/drag-drop';
import { NgIf } from '@angular/common';
import { Component, Inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Model,
  ModelService,
} from 'src/app/projects/models/service/model.service';

@Component({
  selector: 'app-reorder-models',
  templateUrl: './reorder-models-dialog.component.html',
  styles: [
    '.cdk-drag-placeholder { opacity: 0; }',
    '.cdk-drag-animating { transition: transform 250ms cubic-bezier(0, 0, 0.2, 1); }',
  ],
  standalone: true,
  imports: [CdkDropList, CdkDrag, MatIcon, NgIf, MatButton],
})
export class ReorderModelsDialogComponent {
  constructor(
    public modelService: ModelService,
    private dialogRef: MatDialogRef<ReorderModelsDialogComponent>,
    private toastService: ToastService,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; models: Model[] },
  ) {
    this.models = [...data.models];
  }

  models: Model[];

  drop(event: CdkDragDrop<Model[]>): void {
    moveItemInArray(this.models, event.previousIndex, event.currentIndex);
  }

  async reorderModels() {
    const modelsToPatch = this.models.map((model, index) => {
      return {
        modelSlug: model.slug,
        patchModel: { display_order: index + 1 },
      };
    });

    this.modelService
      .updateModels(this.data.projectSlug, modelsToPatch)
      .subscribe(() => {
        this.toastService.showSuccess(
          `Model order updated`,
          `Successfully reordered models in project ${this.data.projectSlug}`,
        );
        this.dialogRef.close();
      });
  }
}
