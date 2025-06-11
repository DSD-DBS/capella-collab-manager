/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, DatePipe, NgClass, TitleCasePipe } from '@angular/common';
import { Component, inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RouterLink } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { combineLatest } from 'rxjs';
import { filter, switchMap, take } from 'rxjs/operators';
import { RelativeTimeComponent } from 'src/app/general/relative-time/relative-time.component';
import {
  PipelineEvent,
  PipelineLogLine,
  PipelineRunStatus,
  ProjectsModelsBackupsService,
} from 'src/app/openapi';
import { PipelineRunWrapperService } from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { PipelineWrapperService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { TextLineSkeletonLoaderComponent } from '../../../../helpers/skeleton-loaders/text-line-skeleton-loader/text-line-skeleton-loader.component';

@UntilDestroy()
@Component({
  selector: 'app-view-dialog',
  templateUrl: './view-logs.component.html',
  imports: [
    TextLineSkeletonLoaderComponent,
    AsyncPipe,
    TitleCasePipe,
    RelativeTimeComponent,
    RouterLink,
    MatIconModule,
    NgClass,
    MatTooltipModule,
    MatIconModule,
    DatePipe,
    NgxSkeletonLoaderModule,
  ],
  styles: `
    @reference '../../../../../styles.css';

    .error {
      @apply bg-error;
    }

    .warning {
      @apply bg-warning;
    }

    .success {
      @apply bg-success;
    }

    .primary {
      @apply bg-primary;
    }
  `,
})
export class ViewLogsComponent {
  private modelService = inject(ModelWrapperService);
  private projectService = inject(ProjectWrapperService);
  private pipelineService = inject(PipelineWrapperService);
  pipelineRunService = inject(PipelineRunWrapperService);
  private pipelinesService = inject(ProjectsModelsBackupsService);

  constructor() {
    this.refreshLogs();
    this.refreshEvents();
  }

  logs?: PipelineLogLine[] = undefined;
  events?: PipelineEvent[] = undefined;

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
        next: (res) => (this.events = res),
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
        next: (res) => (this.logs = res),
      });
  }

  get sortedEvents(): PipelineEvent[] | undefined {
    if (!this.events) return undefined;
    return [...this.events].sort(
      (a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
    );
  }

  getColorForPipelineRunStatus(
    status: PipelineRunStatus,
  ): DisplayPipelineState {
    switch (status) {
      case PipelineRunStatus.Pending:
        return {
          info: 'The pipeline run has been triggered and is waiting for the scheduler to pick it up.',
          css: 'warning',
          icon: 'schedule',
        };
      case PipelineRunStatus.Scheduled:
        return {
          info: 'The scheduler has picked up the job and is starting the execution soon.',
          css: 'warning',
          icon: 'timer',
        };
      case PipelineRunStatus.Running:
        return {
          info: 'The pipeline is running. For more information, check the events & logs.',
          css: 'primary',
          icon: 'play_arrow',
        };
      case PipelineRunStatus.Success:
        return {
          info: 'The pipeline run has finished successfully.',
          css: 'success',
          icon: 'check_circle',
        };
      case PipelineRunStatus.Timeout:
        return {
          info: 'The pipeline run has timed out. The job took too long to complete.',
          css: 'error',
          icon: 'timer_off',
        };
      case PipelineRunStatus.Failure:
        return {
          info: 'The pipeline run has failed. Check the logs and events for more information.',
          css: 'error',
          icon: 'error',
        };
    }

    return {
      info: [
        "We're not sure what happened here.",
        "Rerun the pipeline and contact support if the status doesn't change.",
      ].join(' '),
      css: 'primary',
      icon: 'help',
    };
  }
}

export interface ViewLogsData {
  projectSlug: string;
  modelSlug: string;
  job_id: string;
  backup_id: number;
}

export interface DisplayPipelineState {
  info?: string | undefined;
  css: string;
  icon: string;
}
