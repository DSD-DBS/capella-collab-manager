/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, NgFor, NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest } from 'rxjs';
import { filter, switchMap, take } from 'rxjs/operators';
import { ProjectsModelsBackupsService } from 'src/app/openapi';
import { PipelineRunWrapperService } from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { PipelineWrapperService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { TextLineSkeletonLoaderComponent } from '../../../../helpers/skeleton-loaders/text-line-skeleton-loader/text-line-skeleton-loader.component';

@UntilDestroy()
@Component({
  selector: 'app-view-logs-dialog',
  templateUrl: './view-logs-dialog.component.html',
  styleUrls: ['./view-logs-dialog.component.css'],
  // eslint-disable-next-line @typescript-eslint/no-deprecated
  imports: [TextLineSkeletonLoaderComponent, AsyncPipe, NgIf, NgFor],
})
export class ViewLogsDialogComponent {
  private modelService = inject(ModelWrapperService);
  private projectService = inject(ProjectWrapperService);
  private pipelineService = inject(PipelineWrapperService);
  pipelineRunService = inject(PipelineRunWrapperService);
  private pipelinesService = inject(ProjectsModelsBackupsService);

  constructor() {
    this.refreshLogs();
    this.refreshEvents();
  }

  logs?: string = undefined;
  events?: string = undefined;

  refreshEvents(): void {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean), take(1)),
      this.modelService.model$.pipe(filter(Boolean), take(1)),
      this.pipelineService.pipeline$.pipe(filter(Boolean), take(1)),
      this.pipelineRunService.pipelineRun$.pipe(filter(Boolean)),
    ])
      .pipe(
        untilDestroyed(this),
        switchMap(([project, model, pipeline, pipelineRun]) => {
          return this.pipelinesService.getPipelineRunEvents(
            project.slug,
            pipelineRun.id,
            pipeline.id,
            model.slug,
          );
        }),
      )
      .subscribe({
        next: (res: string) => (this.events = res),
        error: () => (this.events = "Couldn't fetch events"),
      });
  }

  refreshLogs(): void {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
      this.pipelineService.pipeline$.pipe(filter(Boolean)),
      this.pipelineRunService.pipelineRun$.pipe(filter(Boolean)),
    ])
      .pipe(
        untilDestroyed(this),
        switchMap(([project, model, pipeline, pipelineRun]) =>
          this.pipelinesService.getLogs(
            project.slug,
            pipelineRun.id,
            pipeline.id,
            model.slug,
          ),
        ),
      )
      .subscribe({
        next: (res: string) => (this.logs = res),
        error: () => (this.logs = "Couldn't fetch logs"),
      });
  }
}

export interface ViewLogsData {
  projectSlug: string;
  modelSlug: string;
  job_id: string;
  backup_id: number;
}
