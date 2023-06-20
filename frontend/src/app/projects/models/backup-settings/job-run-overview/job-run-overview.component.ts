/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, switchMap } from 'rxjs';
import { PipelineRunService } from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { PipelineService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-job-run-overview',
  templateUrl: './job-run-overview.component.html',
  styleUrls: ['./job-run-overview.component.css'],
})
@UntilDestroy()
export class JobRunOverviewComponent implements OnInit {
  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    public pipelineRunService: PipelineRunService,
    private projectService: ProjectService,
    private modelService: ModelService,
    private pipelineService: PipelineService
  ) {}

  ngOnInit() {
    combineLatest([
      this.projectService.project.pipe(filter(Boolean)),
      this.modelService.model.pipe(filter(Boolean)),
      this.pipelineService.pipeline.pipe(filter(Boolean)),
    ])
      .pipe(
        untilDestroyed(this),
        switchMap(([project, model, pipeline]) =>
          this.pipelineRunService.loadPipelineRuns(
            project.slug,
            model.slug,
            pipeline.id
          )
        )
      )
      .subscribe();
  }

  openLogs(id: number) {
    this.router.navigate(['..', 'run', id, 'logs'], {
      relativeTo: this.activatedRoute,
    });
  }
}
