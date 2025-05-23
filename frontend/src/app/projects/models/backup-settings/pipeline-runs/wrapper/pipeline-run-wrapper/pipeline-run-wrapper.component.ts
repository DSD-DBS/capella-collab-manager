/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnDestroy, inject } from '@angular/core';
import { ActivatedRoute, RouterOutlet } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, map, switchMap, take, tap, timer } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { PipelineRunWrapperService } from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { PipelineWrapperService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-pipeline-run-wrapper',
  templateUrl: './pipeline-run-wrapper.component.html',
  styleUrls: ['./pipeline-run-wrapper.component.css'],
  imports: [RouterOutlet],
})
@UntilDestroy()
export class PipelineRunWrapperComponent implements OnDestroy {
  private pipelineService = inject(PipelineWrapperService);
  private pipelineRunService = inject(PipelineRunWrapperService);
  private modelService = inject(ModelWrapperService);
  private projectService = inject(ProjectWrapperService);
  private route = inject(ActivatedRoute);
  private breadcrumbsService = inject(BreadcrumbsService);

  constructor() {
    // Reset pipeline runs on pipeline or pipelineRunID change
    combineLatest([
      this.pipelineService.pipeline$.pipe(
        filter((pipeline) => pipeline === undefined),
      ),
      this.route.params.pipe(
        filter((params) => params?.pipelineRun === undefined),
      ),
    ]).subscribe(() => {
      this.pipelineRunService.resetPipelineRun();
    });

    // If the last pipeline run was finished, don't update anymore.
    timer(0, 2000)
      .pipe(
        switchMap(() => this.pipelineRunService.pipelineRun$.pipe(take(1))),
        filter(
          (pipelineRun) =>
            !(
              pipelineRun &&
              this.pipelineRunService.pipelineRunIsFinished(pipelineRun.status)
            ),
        ),
        tap(() => this.updatePipelineRun()),
        untilDestroyed(this),
      )
      .subscribe();
  }

  updatePipelineRun() {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
      this.pipelineService.pipeline$.pipe(filter(Boolean)),
      this.route.params.pipe(map((params) => params.pipelineRun as number)),
    ])
      .pipe(untilDestroyed(this), take(1))
      .subscribe(([project, model, pipeline, pipelineRunID]) =>
        this.pipelineRunService.loadPipelineRun(
          project.slug,
          model.slug,
          pipeline.id,
          pipelineRunID,
        ),
      );
  }

  ngOnDestroy(): void {
    this.breadcrumbsService.updatePlaceholder({ pipelineRun: undefined });
    this.pipelineRunService.resetPipelineRun();
  }
}
