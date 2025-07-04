/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, DatePipe, KeyValuePipe } from '@angular/common';
import {
  AfterViewInit,
  Component,
  ElementRef,
  QueryList,
  ViewChildren,
  OnInit,
  inject,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
import { PipelineRunWrapperService } from 'src/app/projects/models/backup-settings/pipeline-runs/service/pipeline-run.service';
import { PipelineWrapperService } from 'src/app/projects/models/backup-settings/service/pipeline.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { TextLineSkeletonLoaderComponent } from '../../../../helpers/skeleton-loaders/text-line-skeleton-loader/text-line-skeleton-loader.component';

@Component({
  selector: 'app-job-run-overview',
  templateUrl: './job-run-overview.component.html',
  imports: [TextLineSkeletonLoaderComponent, AsyncPipe, DatePipe, KeyValuePipe],
})
@UntilDestroy()
export class JobRunOverviewComponent implements OnInit, AfterViewInit {
  pipelineRunService = inject(PipelineRunWrapperService);
  private router = inject(Router);
  private activatedRoute = inject(ActivatedRoute);
  private projectService = inject(ProjectWrapperService);
  private modelService = inject(ModelWrapperService);
  private pipelineService = inject(PipelineWrapperService);

  pageSize = 25;
  pageSizeArray = [...Array(this.pageSize).keys()];

  @ViewChildren('page', { read: ElementRef })
  pageElements?: QueryList<ElementRef>;

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
    this.router.navigate(['..', 'run', id], {
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
