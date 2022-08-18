// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  constructor(private http: HttpClient) {}

  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';

  base_url = new URL('projects/', environment.backend_url + '/');

  projects: Array<Project> | undefined;
  project: Project | undefined;

  init(project_slug: string): Observable<Project> {
    if (!this.project || !(this.project.slug === project_slug)) {
      this.project = undefined;
      return this.getProjectBySlug(project_slug);
    }
    return of(this.project);
  }

  initAll(): Observable<Project[]> {
    if (this.projects) return of(this.projects);
    return this.list();
  }

  getProjectBySlug(slug: string): Observable<Project> {
    let url = new URL('details/', this.base_url);
    return new Observable<Project>((subscriber) => {
      this.http
        .get<Project>(url.toString(), { params: { slug } })
        .subscribe((project) => {
          this.project = project;
          subscriber.next(project);
          subscriber.complete();
        });
    });
  }

  list(): Observable<Project[]> {
    return new Observable<Project[]>((subscriber) => {
      this.http
        .get<Array<Project>>(this.BACKEND_URL_PREFIX)
        .subscribe((projects) => {
          this.projects = projects;
          subscriber.next(projects);
          subscriber.complete();
        });
    });
  }

  getProject(name: string): Observable<Project> {
    return this.http.get<Project>(this.BACKEND_URL_PREFIX + name);
  }

  updateDescription(name: string, description: string): Observable<Project> {
    let url = new URL(name, this.base_url);
    return new Observable<Project>((subscriber) => {
      this.http
        .patch<Project>(url.toString(), { description })
        .subscribe((project) => {
          this.project = project;
          subscriber.next(project);
          subscriber.complete();
        });
    });
  }

  createProject(name: string): Observable<Project> {
    return new Observable<Project>((subscriber) => {
      this.http
        .post<Project>(this.BACKEND_URL_PREFIX, {
          name,
        })
        .subscribe((project) => {
          this.project = project;
          this.list().subscribe();
          subscriber.next(project);
          subscriber.complete();
        });
    });
  }

  deleteProject(project_name: string): Observable<any> {
    return this.http.delete<any>(this.BACKEND_URL_PREFIX + project_name);
  }

  stageForProjectDeletion(project_name: string): Observable<any> {
    return this.http.patch<any>(
      this.BACKEND_URL_PREFIX + `${project_name}/stage`,
      {}
    );
  }
}

export interface UserMetadata {
  leads: number;
  contributors: number;
  subscribers: number;
}

export interface Project {
  name: string;
  slug: string;
  staged_by: string;
  description: string;
  users: UserMetadata;
}

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
