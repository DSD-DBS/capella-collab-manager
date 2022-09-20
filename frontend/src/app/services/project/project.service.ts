/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, map } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';
  base_url = new URL('projects/', environment.backend_url + '/');

  _project = new BehaviorSubject<Project | undefined>(undefined);
  _projects = new BehaviorSubject<Project[] | undefined>(undefined);

  get project() {
    return this._project.value;
  }
  get projects() {
    return this._projects.value;
  }

  constructor(private http: HttpClient) {}

  getProjectBySlug(slug: string): Observable<Project> {
    let url = new URL('details/', this.base_url);
    return this.http.get<Project>(url.toString(), { params: { slug } });
  }

  list(): Observable<Project[]> {
    return this.http.get<Project[]>(this.BACKEND_URL_PREFIX);
  }

  listStagedProjects(): Observable<Project[]> {
    return this.list().pipe(
      map((projects) => projects.filter((project) => project.staged_by))
    );
  }

  getProject(name: string): Observable<Project> {
    return this.http.get<Project>(this.BACKEND_URL_PREFIX + name);
  }

  updateDescription(name: string, description: string): Observable<Project> {
    let url = new URL(name, this.base_url);
    return this.http.patch<Project>(url.toString(), { description });
  }

  createProject(project: {
    name: string;
    description: string;
  }): Observable<Project> {
    return this.http.post<Project>(this.BACKEND_URL_PREFIX, project);
  }

  deleteProject(project_name: string): Observable<any> {
    return this.http.delete<any>(this.BACKEND_URL_PREFIX + project_name);
  }

  stageForProjectDeletion(project_slug: string): Observable<{}> {
    const url = new URL(`${project_slug}/stage`, this.base_url);
    return this.http.patch<{}>(url.toString(), null);
  }

  unstageProject(project_slug: string): Observable<Project> {
    const url = new URL(`${project_slug}/unstage`, this.base_url);
    return this.http.patch<Project>(url.toString(), null);
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
  staged_by: { name: string };
  description: string;
  users_metadata: UserMetadata;
}

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
