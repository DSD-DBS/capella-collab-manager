/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { BehaviorSubject, filter, switchMap, take, tap } from 'rxjs';
import { ProjectsToolsService, ProjectTool } from 'src/app/openapi';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';

@UntilDestroy()
@Injectable({
  providedIn: 'root',
})
export class ProjectToolsWrapperService {
  projectWrapperService = inject(ProjectWrapperService);
  private projectToolService = inject(ProjectsToolsService);

  private readonly _projectTools = new BehaviorSubject<
    ProjectTool[] | undefined
  >(undefined);
  readonly projectTools$ = this._projectTools.asObservable();

  loadProjectTools(): void {
    this._projectTools.next(undefined);
    this.projectWrapperService.project$
      .pipe(
        filter(Boolean),
        switchMap((project) => {
          return this.projectToolService.getProjectTools(project.slug);
        }),
        untilDestroyed(this),
        take(1),
        tap((tools) => {
          this._projectTools.next(tools);
        }),
      )
      .subscribe();
  }
}
