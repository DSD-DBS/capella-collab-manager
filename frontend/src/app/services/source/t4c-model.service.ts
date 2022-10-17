/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { T4CInstance } from '../settings/t4c-model.service';
import { T4CRepository } from '../../settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Injectable({
  providedIn: 'root',
})
export class T4cModelService {
  constructor(private http: HttpClient) {}

  _t4cModel = new BehaviorSubject<T4CModel | undefined>(undefined);
  get t4cModel() {
    return this._t4cModel.value;
  }

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

  getT4CModel(
    project_slug: string,
    model_slug: string,
    id: number
  ): Observable<T4CModel> {
    return this.http
      .get<T4CModel>(this.urlFactory(project_slug, model_slug) + id + '/')
      .pipe(tap(console.log));
  }

  createT4CModel(
    project_slug: string,
    model_slug: string,
    body: SubmitT4CModel
  ): Observable<null> {
    return this.http.post<null>(
      this.urlFactory(project_slug, model_slug),
      body
    );
  }

  editT4CModel(
    project_slug: string,
    model_slug: string,
    body: SubmitT4CModel
  ): Observable<null> {
    return this.http.patch<null>(
      this.urlFactory(project_slug, model_slug),
      body
    );
  }
}

export type SubmitT4CModel = {
  t4c_instance_id: number;
  t4c_repository_id: number;
  name: string;
};

export type T4CModel = {
  name: string;
  id: number;
  repository: T4CRepository;
};
