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
  project: Project | null = null;

  getProjects(): Observable<Array<Project>> {
    return this.http.get<Array<Project>>(this.BACKEND_URL_PREFIX);
  }

  getProject(name: string): Observable<Project> {
    return this.http.get<Project>(this.BACKEND_URL_PREFIX + name);
  }

  refreshProjects(): void {
    this.getProjects().subscribe((res) => {
      this.projects = res;
    });
  }

  updateDescription(name: string, description: string): Observable<Project> {
    return this.http.patch<Project>(this.BACKEND_URL_PREFIX + name, {
      description,
    });
  }

  createProject(name: string): Observable<Project> {
    return this.http.post<Project>(this.BACKEND_URL_PREFIX, {
      name,
    });
  }
}

export interface UserMetadata {
  leads: number;
  contributors: number;
  subscribers: number;
}

export interface Project {
  name: string;
  description: string;
  users: UserMetadata;
}

export type EditingMode = 't4c' | 'git';
export type ProjectType = 'project' | 'library';
