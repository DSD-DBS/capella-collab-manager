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

  listT4CModels(
    project_slug: string,
    model_slug: string,
    t4c_instance_id: number,
    t4c_repository_id: number
  ): Observable<T4CModel[]> {
    return this.http.get<T4CModel[]>(
      this.urlFactory(project_slug, model_slug),
      { params: { t4c_instance_id, t4c_repository_id } }
    );
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

export type T4CModel = {
  t4c_instance_id: number;
  t4c_repository_id: number;
  name: string;
  id: number;
};
