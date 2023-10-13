/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  AfterViewInit,
  Component,
  ElementRef,
  QueryList,
  ViewChildren,
  OnInit,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
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
export class JobRunOverviewComponent implements OnInit, AfterViewInit {
  pageSize = 25;
  pageSizeArray = [...Array(this.pageSize).keys()];

  @ViewChildren('page', { read: ElementRef })
  pageElements?: QueryList<ElementRef>;

  constructor(
    public pipelineRunService: PipelineRunService,
    private router: Router,
    private activatedRoute: ActivatedRoute,
    private projectService: ProjectService,
    private modelService: ModelService,
    private pipelineService: PipelineService,
  ) {}

  ngOnInit() {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
      this.pipelineService.pipeline$.pipe(filter(Boolean)),
    ]).subscribe(([project, model, pipeline]) => {
      this.pipelineRunService.loadPipelineRuns(
        project.slug,
        model.slug,
        pipeline.id,
        1,
        this.pageSize,
      );
    });
  }

  ngAfterViewInit(): void {
    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
      this.pipelineService.pipeline$.pipe(filter(Boolean)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model, pipeline]) => {
        this.observeVisibleJobs(project.slug, model.slug, pipeline.id);
      });
  }

  openLogs(id: number) {
    this.router.navigate(['..', 'run', id, 'logs'], {
      relativeTo: this.activatedRoute,
    });
  }

  observeVisibleJobs(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
  ) {
    const observer = new IntersectionObserver(
      (entries: IntersectionObserverEntry[], _: IntersectionObserver) => {
        entries
          .filter((entry) => entry.isIntersecting) // Only visible elements
          .filter((entry) => entry.target.id !== '1') // Initial page is pre-loaded in ngOnInit
          .forEach((entry) => {
            this.pipelineRunService.loadPipelineRuns(
              projectSlug,
              modelSlug,
              pipelineID,
              parseInt(entry.target.id),
              this.pageSize,
            );
          });
      },
      {
        root: null,
        threshold: 0.1,
      },
    );

    this.pageElements?.changes.subscribe((res) => {
      res.forEach((pageElement: ElementRef) => {
        observer.observe(pageElement.nativeElement);
      });
    });
  }
}
