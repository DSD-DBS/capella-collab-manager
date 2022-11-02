/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Model } from 'src/app/services/model/model.service';

@Component({
  selector: 'app-trigger-pipeline',
  templateUrl: './trigger-pipeline.component.html',
  styleUrls: ['./trigger-pipeline.component.css'],
})
export class TriggerPipelineComponent {
  pipelines: Pipeline[] = [{ id: 1 }, { id: 2 }];
  selectedPipeline?: Pipeline = undefined;

  configurationForm = new FormGroup({
    includeHistory: new FormControl(false),
  });

  constructor(
    private toastService: ToastService,
    private dialogRef: MatDialogRef<TriggerPipelineComponent>,
    @Inject(MAT_DIALOG_DATA) public model: Model
  ) {}

  selectPipeline(pipeline: Pipeline) {
    this.selectedPipeline = pipeline;
  }

  runPipeline() {
    this.toastService.showSuccess(
      'Pipeline triggered',
      'You can check the current status in the pipeline settings.'
    );
    this.dialogRef.close();
  }

  estimateTime(): string {
    if (this.configurationForm.value.includeHistory) {
      return '1-6 hours';
    } else {
      return '5-10 minutes';
    }
  }

  closeDialog(): void {
    this.dialogRef.close();
  }
}

export type Pipeline = {
  id: number;
};
