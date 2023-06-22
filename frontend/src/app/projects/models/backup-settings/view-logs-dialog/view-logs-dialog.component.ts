/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest } from 'rxjs';
import { filter, switchMap } from 'rxjs/operators';
import { PipelineRunService } from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { PipelineService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-view-logs-dialog',
  templateUrl: './view-logs-dialog.component.html',
  styleUrls: ['./view-logs-dialog.component.css'],
})
export class ViewLogsDialogComponent {
  constructor(
    private modelService: ModelService,
    private projectService: ProjectService,
    private pipelineService: PipelineService,
    public pipelineRunService: PipelineRunService
  ) {
    this.refreshLogs();
    this.refreshEvents();
  }

  logs = '';
  events = '';

  refreshEvents(): void {
    combineLatest([
      this.projectService.project.pipe(filter(Boolean)),
      this.modelService.model.pipe(filter(Boolean)),
      this.pipelineService.pipeline.pipe(filter(Boolean)),
      this.pipelineRunService.pipelineRun.pipe(filter(Boolean)),
    ])
      .pipe(
        untilDestroyed(this),
        switchMap(([project, model, pipeline, pipelineRun]) =>
          this.pipelineRunService.getEvents(
            project.slug,
            model.slug,
            pipeline.id,
            pipelineRun.id
          )
        )
      )
      .subscribe({
        next: (res: string) => {
          this.events = res;
        },
        error: () => {
          this.events = "Couldn't fetch events";
        },
      });
  }

  refreshLogs(): void {
    combineLatest([
      this.projectService.project.pipe(filter(Boolean)),
      this.modelService.model.pipe(filter(Boolean)),
      this.pipelineService.pipeline.pipe(filter(Boolean)),
      this.pipelineRunService.pipelineRun.pipe(filter(Boolean)),
    ])
      .pipe(
        untilDestroyed(this),
        switchMap(([project, model, pipeline, pipelineRun]) =>
          this.pipelineRunService.getLogs(
            project.slug,
            model.slug,
            pipeline.id,
            pipelineRun.id
          )
        )
      )
      .subscribe({
        next: (res: string) => {
          this.logs = res;
        },
        error: () => {
          this.logs = "Couldn't fetch logs";
        },
      });
  }
}

export type ViewLogsData = {
  projectSlug: string;
  modelSlug: string;
  job_id: string;
  backup_id: number;
};
