// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  constructor(private http: HttpClient) {}
  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';

  projects: Array<Project> = [];

  getProjects(): Observable<Array<Project>> {
    return this.http.get<Array<Project>>(this.BACKEND_URL_PREFIX);
  }

  refreshRepositories(): void {
    this.getProjects().subscribe((res) => {
      this.projects = res;
    });
  }

  createRepository(name: string): Observable<Project> {
    return this.http.post<Project>(this.BACKEND_URL_PREFIX, {
      name,
    });
  }
}

export interface Project {
  name: string;
  description: string;
  editing_mode: EditingMode;
  type: ProjectType;
}

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
