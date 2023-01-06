/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { T4CRepository } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CModelService {
  constructor(private http: HttpClient) {}

  _t4cModel = new BehaviorSubject<T4CModel | undefined>(undefined);
  get t4cModel() {
    return this._t4cModel.value;
  }

  _t4cModels = new BehaviorSubject<T4CModel[] | undefined>(undefined);
  get t4cModels() {
    return this._t4cModels.value;
  }

  urlFactory(project_slug: string, model_slug: string): string {
    return `${environment.backend_url}/projects/${project_slug}/models/${model_slug}/modelsources/t4c`;
  }

  listT4CModels(
    project_slug: string,
    model_slug: string
  ): Observable<T4CModel[]> {
    return this.http
      .get<T4CModel[]>(this.urlFactory(project_slug, model_slug))
      .pipe(tap((models) => this._t4cModels.next(models)));
  }

  getT4CModel(
    project_slug: string,
    model_slug: string,
    id: number
  ): Observable<T4CModel> {
    return this.http.get<T4CModel>(
      `${this.urlFactory(project_slug, model_slug)}/${id}`
    );
  }

  createT4CModel(
    project_slug: string,
    model_slug: string,
    body: SubmitT4CModel
  ): Observable<T4CModel> {
    return this.http.post<T4CModel>(this.urlFactory(project_slug, model_slug), {
      t4c_instance_id: body.t4cInstanceId,
      t4c_repository_id: body.t4cRepositoryId,
      name: body.name,
    });
  }

  patchT4CModel(
    project_slug: string,
    model_slug: string,
    t4c_model_id: number,
    body: SubmitT4CModel
  ): Observable<T4CModel> {
    return this.http.patch<T4CModel>(
      `${this.urlFactory(project_slug, model_slug)}/${t4c_model_id}`,
      {
        t4c_instance_id: body.t4cInstanceId,
        t4c_repository_id: body.t4cRepositoryId,
        name: body.name,
      }
    );
  }

  unlinkT4CModel(
    projectSlug: string,
    modelSlug: string,
    t4cModelId: number
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.urlFactory(projectSlug, modelSlug)}/${t4cModelId}`
    );
  }

  clear() {
    this._t4cModels.next(undefined);
    this._t4cModel.next(undefined);
  }
}

export type SubmitT4CModel = {
  t4cInstanceId: number;
  t4cRepositoryId: number;
  name: string;
};

export type T4CModel = {
  name: string;
  id: number;
  repository: T4CRepository;
};

export type SimpleT4CModel = {
  project_name: string;
  repository_name: string;
  instance_name: string;
};
