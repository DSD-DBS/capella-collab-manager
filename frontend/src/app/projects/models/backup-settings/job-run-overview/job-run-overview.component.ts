/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ChangeDetectorRef, Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { combineLatest, filter, switchMap } from 'rxjs';
import {
  PipelineRun,
  PipelineRunService,
} from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { PipelineService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';

@Component({
  selector: 'app-job-run-overview',
  templateUrl: './job-run-overview.component.html',
  styleUrls: ['./job-run-overview.component.css'],
})
export class JobRunOverviewComponent {
  jobRuns?: PipelineRun[] = [];

  constructor(
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private projectService: ProjectService,
    private modelService: ModelService,
    private pipelineRunService: PipelineRunService,
    private pipelineService: PipelineService,
    private changeDetectorRef: ChangeDetectorRef
  ) {
    this.fetchJobRuns();
  }

  fetchJobRuns() {
    combineLatest([
      this.projectService.project.pipe(filter(Boolean)),
      this.modelService.model.pipe(filter(Boolean)),
      this.pipelineService.pipeline.pipe(filter(Boolean)),
    ])
      .pipe(
        switchMap(([project, model, pipeline]) =>
          this.pipelineRunService.getRunsOfPipeline(
            project.slug,
            model.slug,
            pipeline.id
          )
        )
      )
      .subscribe((jobRuns) => {
        this.jobRuns = jobRuns;
      });
  }

  openLogs(id: number) {
    this.router.navigate(['..', 'run', id, 'logs'], {
      relativeTo: this.activatedRoute,
    });
  }
}
