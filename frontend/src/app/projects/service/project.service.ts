/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { BehaviorSubject, map, Observable, take, tap } from 'rxjs';
import slugify from 'slugify';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  BACKEND_URL_PREFIX = environment.backend_url + '/projects';

  constructor(private http: HttpClient) {}

  private _project = new BehaviorSubject<Project | undefined>(undefined);
  private _projects = new BehaviorSubject<Project[] | undefined>(undefined);

  public readonly project$ = this._project.asObservable();
  public readonly projects$ = this._projects.asObservable();

  loadProjects(): void {
    this.http.get<Project[]>(this.BACKEND_URL_PREFIX).subscribe({
      next: (projects) => this._projects.next(projects),
      error: () => this._projects.next(undefined),
    });
  }

  loadProjectBySlug(slug: string): void {
    this.http.get<Project>(`${this.BACKEND_URL_PREFIX}/${slug}`).subscribe({
      next: (project) => this._project.next(project),
      error: () => this._project.next(undefined),
    });
  }

  createProject(project: PostProject): Observable<Project> {
    return this.http.post<Project>(this.BACKEND_URL_PREFIX, project).pipe(
      tap({
        next: (project) => {
          this.loadProjects();
          this._project.next(project);
        },
        error: () => this._project.next(undefined),
      })
    );
  }

  updateProject(
    project_slug: string,
    project: PatchProject
  ): Observable<Project> {
    return this.http
      .patch<Project>(`${this.BACKEND_URL_PREFIX}/${project_slug}`, project)
      .pipe(
        tap({
          next: (project) => {
            this.loadProjects();
            this._project.next(project);
          },
          error: () => this._project.next(undefined),
        })
      );
  }

  deleteProject(projectSlug: string): Observable<void> {
    return this.http
      .delete<void>(`${this.BACKEND_URL_PREFIX}/${projectSlug}`)
      .pipe(
        tap(() => {
          this.loadProjects();
          this._project.next(undefined);
        })
      );
  }

  clearProject(): void {
    this._project.next(undefined);
  }

  asyncSlugValidator(ignoreProject?: Project): AsyncValidatorFn {
    const ignoreSlug = !!ignoreProject ? ignoreProject.slug : -1;
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      const projectSlug = slugify(control.value, { lower: true });
      return this.projects$.pipe(
        take(1),
        map((projects) => {
          return projects?.find(
            (project) =>
              project.slug === projectSlug && project.slug !== ignoreSlug
          )
            ? { uniqueSlug: { value: projectSlug } }
            : null;
        })
      );
    };
  }

  getProjectVisibilityDescription(visibility: ProjectVisibility): string {
    return ProjectVisibility[visibility];
  }

  getAvailableVisibilities(): ProjectVisibility[] {
    return Object.keys(ProjectVisibility) as ProjectVisibility[];
  }
}

export type UserMetadata = {
  leads: number;
  contributors: number;
  subscribers: number;
};

export type PostProject = {
  name: string;
  description: string;
  visibility: ProjectVisibility;
};

export type PatchProject = Partial<PostProject> & {
  is_archived?: boolean;
};

export type ProjectVisibility = 'internal' | 'private';

export type Project = Required<PatchProject> & {
  slug: string;
  users: UserMetadata;
};

export const ProjectVisibility = {
  internal:
    'Internal - all logged in users can see the project and have read access on its models.',
  private:
    'Private - users need to be explicitly granted access to see the project.',
};
