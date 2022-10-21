/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface BaseGitModel {
  path: string;
  revision: string;
  entrypoint: string;
  username: string;
}

export interface CreateGitModel extends BaseGitModel {
  password?: string;
}

export interface PatchGitModel extends CreateGitModel {
  primary: boolean;
}

export interface GetGitModel extends BaseGitModel {
  id: number;
  primary: boolean;
  password: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class SourceService {
  constructor(private http: HttpClient) {}

  addGitSource(
    project_slug: string,
    model_slug: string,
    source: CreateGitModel
  ): Observable<GetGitModel> {
    return this.http.post<GetGitModel>(
      environment.backend_url +
        `/projects/${project_slug}/models/${model_slug}/git/`,
      source
    );
  }
}
