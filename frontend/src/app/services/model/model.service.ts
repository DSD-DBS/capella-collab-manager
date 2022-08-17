/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, single } from 'rxjs';
import { ProjectService } from 'src/app/services/project/project.service';
import { environment } from 'src/environments/environment';

export interface NewModel {
  name: string;
  description: string;
  tool_id: number;
}

export interface EmptyModel extends NewModel {
  tool_id: number;
  version_id: string;
  type_id: string;
}

export interface GitModel extends NewModel {
  url: string;
  username: string;
  password: string;
  revision: string;
  path: string;
  entrypoint: string;
}

export interface OfflineModel extends NewModel {}

export interface Model {
  id: number;
  project_slug: string;
  slug: string;
  name: string;
  description: string;
  tool_id: number | null;
  version_id: number | null;
  type_id: number | null;
  t4c_model: number | null;
  git_model: number | null;
}

@Injectable({
  providedIn: 'root',
})
export class ModelService {
  base_url = new URL('models/', environment.backend_url + '/');

  constructor(
    private http: HttpClient,
    private projectService: ProjectService
  ) {}

  _model: BehaviorSubject<Model | undefined> = new BehaviorSubject<
    Model | undefined
  >(undefined);
  _models: BehaviorSubject<Model[] | undefined> = new BehaviorSubject<
    Model[] | undefined
  >(undefined);

  get models(): Model[] | undefined {
    return this._models.value;
  }

  get model(): Model | undefined {
    return this._model.value;
  }

  list(project_slug: string): Observable<Model[]> {
    let url = new URL(project_slug, this.base_url);
    return this.http.get<Model[]>(url.toString()).pipe(single());
  }

  getModelBySlug(slug: string, project_slug: string): Observable<Model> {
    let url = new URL(`${project_slug}/details/`, this.base_url);
    return this.http
      .get<Model>(url.toString(), { params: { slug } })
      .pipe(single());
  }

  createNewModel(project_slug: string, model: NewModel): Observable<Model> {
    let url = new URL(project_slug + '/create-new/', this.base_url);
    return this.createModelGeneric(url, model);
  }

  createEmptyModel(project_slug: string, model: EmptyModel): Observable<Model> {
    let url = new URL(project_slug + '/create-empty/', this.base_url);
    return this.createModelGeneric(url, model);
  }

  setToolDetailsForModel(
    project_slug: string,
    model_slug: string,
    version_id: number,
    type_id: number
  ): Observable<Model> {
    let url = new URL(
      `${project_slug}/set-tool-details/${model_slug}/`,
      this.base_url
    );
    return this.http.patch<Model>(url.toString(), { version_id, type_id });
  }

  createModelGeneric<T extends NewModel>(
    url: URL,
    new_model: T
  ): Observable<Model> {
    return this.http.post<Model>(url.toString(), new_model);
  }
}
