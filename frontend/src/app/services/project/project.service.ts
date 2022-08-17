/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  BehaviorSubject,
  dematerialize,
  materialize,
  Observable,
  of,
  single,
  tap,
} from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  constructor(private http: HttpClient) {}

  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';

  base_url = new URL('projects/', environment.backend_url + '/');

  _project: BehaviorSubject<Project | undefined> = new BehaviorSubject<
    Project | undefined
  >(undefined);
  _projects: BehaviorSubject<Project[] | undefined> = new BehaviorSubject<
    Project[] | undefined
  >(undefined);
  get project() {
    return this._project.value;
  }
  get projects() {
    return this._projects.getValue();
  }

  getProjectBySlug(slug: string): Observable<Project> {
    let url = new URL('details/', this.base_url);
    return this.http.get<Project>(url.toString(), { params: { slug } });
  }

  list(): Observable<Project[]> {
    return this.http.get<Project[]>(this.BACKEND_URL_PREFIX).pipe(single());
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
    return this.http
      .post<Project>(this.BACKEND_URL_PREFIX, project)
      .pipe(single());
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
  description: string;
  users: UserMetadata;
}

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
