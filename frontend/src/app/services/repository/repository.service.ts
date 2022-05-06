// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { AuthService } from '../auth/auth.service';

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  constructor(private http: HttpClient, private authService: AuthService) {
    if (this.authService.isLoggedIn()) {
      this.getAndSaveManagerRole();
    }
  }
  BACKEND_URL_PREFIX = environment.backend_url + '/projects/';
  isManager: boolean = false;
  repositories: Array<Project> = [];

  getAndSaveManagerRole(): void {
    this.getProjects().subscribe((res: Array<Project>) => {
      let tmpIsManager = false;
      for (let s of res) {
        if (s.role === 'administrator' || s.role === 'manager') {
          tmpIsManager = true;
        }
      }
      this.isManager = tmpIsManager;
    });
  }

  getProjects(): Observable<Array<Project>> {
    return this.http.get<Array<Project>>(this.BACKEND_URL_PREFIX);
  }

  refreshRepositories(): void {
    this.getProjects().subscribe((res) => {
      this.repositories = res;
    });
  }

  createRepository(name: string): Observable<Project> {
    return this.http.post<Project>(this.BACKEND_URL_PREFIX, {
      name,
    });
  }
}

export type Warnings = 'LICENCE_LIMIT' | 'NO_GIT_MODEL_DEFINED';

export interface Project {
  repository_name: string;
  username: string;
  permissions: Array<'read' | 'write'>;
  warnings: Array<Warnings>;
  role: 'user' | 'manager' | 'administrator';
}
