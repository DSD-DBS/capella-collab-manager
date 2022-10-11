/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface Source {
  path: string;
  entrypoint: string;
  revision: string;
  username?: string;
  password?: string;
}

@Injectable({
  providedIn: 'root',
})
export class SourceService {
  constructor(private http: HttpClient) {}

  source: Source | null = null;
  sources: Source[] | null = null;

  addGitSource(
    project_name: string,
    model_slug: string,
    source: Source
  ): Observable<Source> {
    return this.http.post<Source>(
      environment.backend_url +
        '/projects/' +
        project_name +
        '/models/' +
        model_slug +
        '/git/',
      source
    );
  }
}
