/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, map, switchMap, tap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { PipelineService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-pipeline-wrapper',
  templateUrl: './pipeline-wrapper.component.html',
  styleUrls: ['./pipeline-wrapper.component.css'],
})
@UntilDestroy()
export class PipelineWrapperComponent implements OnInit, OnDestroy {
  constructor(
    private pipelineService: PipelineService,
    private modelService: ModelService,
    private projectService: ProjectService,
    private route: ActivatedRoute,
    private breadcrumbsService: BreadcrumbsService,
  ) {}

  ngOnInit(): void {
    // Reset pipeline runs on pipeline change
    this.modelService.model$.pipe(
      filter((model) => model === undefined),
      tap(() => {
        this.pipelineService.resetPipeline();
        this.pipelineService.resetPipelines();
        return;
      }),
    );

    this.route.params
      .pipe(filter((params) => params.pipeline === undefined))
      .subscribe(() => {
        this.pipelineService.resetPipeline();
      });

    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
      this.route.params.pipe(
        map((params) => params.pipeline as number),
        filter(Boolean),
      ),
    ])
      .pipe(
        untilDestroyed(this),
        switchMap(([project, model, pipelineID]) =>
          this.pipelineService.loadPipeline(
            project!.slug,
            model!.slug,
            pipelineID,
          ),
        ),
      )
      .subscribe();
  }

  ngOnDestroy(): void {
    this.breadcrumbsService.updatePlaceholder({ pipeline: undefined });
    this.pipelineService.resetPipeline();
  }
}
