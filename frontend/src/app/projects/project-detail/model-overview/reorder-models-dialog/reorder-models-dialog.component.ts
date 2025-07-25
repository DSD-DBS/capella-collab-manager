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
import { Component, inject } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ToolModel } from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';

@Component({
  selector: 'app-reorder-models',
  templateUrl: './reorder-models-dialog.component.html',
  styles: `
    .cdk-drag-placeholder {
      opacity: 0;
    }
    .cdk-drag-animating {
      transition: transform 250ms cubic-bezier(0, 0, 0.2, 1);
    }
    .cdk-drop-list-dragging .cdk-drag {
      transition: transform 250ms cubic-bezier(0, 0, 0.2, 1);
    }
  `,
  imports: [CdkDropList, CdkDrag, MatIcon, MatButton],
})
export class ReorderModelsDialogComponent {
  modelService = inject(ModelWrapperService);
  private dialogRef =
    inject<MatDialogRef<ReorderModelsDialogComponent>>(MatDialogRef);
  private toastService = inject(ToastService);
  data = inject<{
    projectSlug: string;
    models: ToolModel[];
  }>(MAT_DIALOG_DATA);

  constructor() {
    const data = this.data;

    this.models = [...data.models];
  }

  models: ToolModel[];

  drop(event: CdkDragDrop<ToolModel[]>): void {
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
