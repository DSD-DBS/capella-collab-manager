/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { Pipeline, ProjectsModelsBackupsService } from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class PipelineWrapperService {
  private breadcrumbsService = inject(BreadcrumbsService);
  private pipelinesService = inject(ProjectsModelsBackupsService);

  private _pipeline = new BehaviorSubject<Pipeline | undefined>(undefined);
  private _pipelines = new BehaviorSubject<Pipeline[] | undefined>(undefined);

  public readonly pipeline$ = this._pipeline.asObservable();
  public readonly pipelines$ = this._pipelines.asObservable();

  resetPipeline() {
    this._pipeline.next(undefined);
  }

  resetPipelines() {
    this._pipelines.next(undefined);
  }

  loadPipeline(
    projectSlug: string,
    modelSlug: string,
    pipelineID: number,
  ): Observable<Pipeline> {
    this._pipeline.next(undefined);
    return this.pipelinesService
      .getPipeline(projectSlug, pipelineID, modelSlug)
      .pipe(
        tap((pipeline) => {
          this._pipeline.next(pipeline);
          this.breadcrumbsService.updatePlaceholder({ pipeline });
        }),
      );
  }

  loadPipelines(
    projectSlug: string,
    modelSlug: string,
  ): Observable<Pipeline[]> {
    this._pipelines.next(undefined);
    return this.pipelinesService.getPipelines(projectSlug, modelSlug).pipe(
      tap((pipelines: Pipeline[]) => {
        this._pipelines.next(pipelines);
      }),
    );
  }
}
