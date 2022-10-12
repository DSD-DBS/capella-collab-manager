/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class T4cModelService {
  constructor(private http: HttpClient) {}

  urlFactory(project_slug: string, model_slug: string): string {
    return `${environment.backend_url}/projects/extensions/modelsources/t4c/project/${project_slug}/model/${model_slug}/`;
  }

  createT4CModel(
    project_slug: string,
    model_slug: string,
    body: CreateT4CModel
  ): Observable<null> {
    return this.http.post<null>(
      this.urlFactory(project_slug, model_slug),
      body
    );
  }
}

export type CreateT4CModel = {
  t4c_instance_id: number;
  t4c_repository_id: number;
  name: string;
};
