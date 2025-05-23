/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, map, Observable, take, tap } from 'rxjs';
import slugify from 'slugify';
import {
  PatchProject,
  PostProjectRequest,
  Project,
  ProjectType,
  ProjectUserRole,
  ProjectVisibility,
  ProjectsService,
  Tag,
  TagScope,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class ProjectWrapperService {
  private projectsService = inject(ProjectsService);

  private _project = new BehaviorSubject<Project | undefined>(undefined);
  private _projects = new BehaviorSubject<Project[] | undefined>(undefined);

  public readonly project$ = this._project.asObservable();
  public readonly projects$ = this._projects.asObservable();

  loadProjects(minimumRole?: ProjectUserRole): void {
    this.projectsService
      .getProjects(minimumRole)
      .pipe(
        tap({
          next: (projects) => this._projects.next(projects),
          error: () => this._projects.next(undefined),
        }),
      )
      .subscribe();
  }

  loadProjectBySlug(slug: string): void {
    this.projectsService.getProjectBySlug(slug).subscribe({
      next: (project) => this._project.next(project),
      error: () => this._project.next(undefined),
    });
  }

  createProject(project: PostProjectRequest): Observable<Project> {
    return this.projectsService.createProject(project).pipe(
      tap({
        next: (project) => {
          this.loadProjects();
          this._project.next(project);
        },
        error: () => this._project.next(undefined),
      }),
    );
  }

  updateProject(
    project_slug: string,
    project: PatchProject,
  ): Observable<Project> {
    return this.projectsService.updateProject(project_slug, project).pipe(
      tap({
        next: (project) => {
          this.loadProjects();
          this._project.next(project);
        },
        error: () => this._project.next(undefined),
      }),
    );
  }

  deleteProject(projectSlug: string): Observable<void> {
    return this.projectsService.deleteProject(projectSlug).pipe(
      tap(() => {
        this.loadProjects();
        this._project.next(undefined);
      }),
    );
  }

  clearProject(): void {
    this._project.next(undefined);
  }

  asyncSlugValidator(ignoreProject?: Project): AsyncValidatorFn {
    const ignoreSlug = ignoreProject ? ignoreProject.slug : -1;
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      const projectSlug = slugify(control.value, { lower: true });
      return this.projects$.pipe(
        take(1),
        map((projects) => {
          return projects?.find(
            (project) =>
              project.slug === projectSlug && project.slug !== ignoreSlug,
          )
            ? { uniqueSlug: { value: projectSlug } }
            : null;
        }),
      );
    };
  }

  getProjectVisibilityDescription(visibility: ProjectVisibility): string {
    return ProjectVisibilityDescriptions[visibility];
  }

  getAvailableVisibilities(): ProjectVisibility[] {
    return Object.keys(ProjectVisibilityDescriptions) as ProjectVisibility[];
  }

  getProjectTypeDescription(type: ProjectType): string {
    return ProjectTypeDescriptions[type];
  }

  getAvailableProjectTypes(): ProjectType[] {
    return Object.keys(ProjectTypeDescriptions) as ProjectType[];
  }
}

export const ProjectVisibilityDescriptions = {
  internal: 'Internal (viewable by all logged in users)',
  private: 'Private (only viewable by project members)',
};

export const ProjectTypeDescriptions = {
  general: 'General (a project that contains related models)',
  training: 'Training (special project containing training material)',
};

export function getProjectTags(project: Project): Tag[] {
  const tags = [...(project.tags || [])];
  if (project.type === 'training') {
    tags.push({
      id: -1,
      name: 'Training',
      description: 'This is a special project containing training material',
      hex_color: '#FF9800',
      icon: 'school',
      scope: TagScope.Project,
    });
  }
  if (project.visibility === 'private') {
    tags.push({
      id: -2,
      name: 'Restricted Visibility',
      description: 'This project is only viewable by project members',
      hex_color: '#70798C',
      icon: 'lock',
      scope: TagScope.Project,
    });
  }
  if (project.visibility === 'internal') {
    tags.push({
      id: -3,
      name: 'Public Visibility',
      description: 'This project is viewable by all logged in users',
      hex_color: '#70798C',
      icon: 'public',
      scope: TagScope.Project,
    });
  }
  if (project.is_archived) {
    tags.push({
      id: -4,
      name: 'Archived',
      description:
        'TeamForCapella repositories of this project will no longer be' +
        ' available in persistent sessions and will no longer be' +
        " synchronized to Git repositories. In addition, it's not possible" +
        ' to create new models in this project.',
      hex_color: '#a52606',
      icon: 'warning',
      scope: TagScope.Project,
    });
  }

  return tags;
}
