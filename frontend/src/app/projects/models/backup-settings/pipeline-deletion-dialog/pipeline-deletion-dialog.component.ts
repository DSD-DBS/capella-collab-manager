/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { DialogRef } from '@angular/cdk/dialog';
import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggle } from '@angular/material/slide-toggle';
import { MatTooltip } from '@angular/material/tooltip';
import { BehaviorSubject } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Backup, ProjectsModelsBackupsService } from 'src/app/openapi';
import { PipelineWrapperService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { OwnUserWrapperService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-pipeline-deletion-dialog',
  imports: [
    CommonModule,
    MatSlideToggle,
    FormsModule,
    MatButtonModule,
    MatTooltip,
    MatIconModule,
  ],
  templateUrl: './pipeline-deletion-dialog.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PipelineDeletionDialogComponent {
  force = false;
  loading = new BehaviorSubject(false);

  constructor(
    public userService: OwnUserWrapperService,
    private dialogRef: DialogRef,
    private toastService: ToastService,
    private pipelinesService: ProjectsModelsBackupsService,
    private pipelineWrapperService: PipelineWrapperService,
    @Inject(MAT_DIALOG_DATA)
    public data: { projectSlug: string; modelSlug: string; backup: Backup },
  ) {}

  onCancel(): void {
    this.dialogRef.close(false);
  }

  removePipeline(): void {
    this.loading.next(true);
    this.pipelinesService
      .deletePipeline(
        this.data.projectSlug,
        this.data.backup.id,
        this.data.modelSlug,
        this.force,
      )
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'Backup pipeline deleted',
            `The pipeline with the ID ${this.data.backup.id} has been deleted`,
          );
          this.loading.next(false);
          this.pipelineWrapperService
            .loadPipelines(this.data.projectSlug, this.data.modelSlug)
            .subscribe();
          this.dialogRef.close(true);
        },
        error: () => {
          this.loading.next(false);
        },
      });
  }
}
