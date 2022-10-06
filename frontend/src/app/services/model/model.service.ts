/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, single } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Tool, ToolType, ToolVersion } from '../tools/tool.service';

export interface NewModel {
  name: string;
  description: string;
  tool_id: number;
}

export interface Model {
  id: number;
  project_slug: string;
  slug: string;
  name: string;
  description: string;
  tool: Tool;
  version: ToolVersion | null;
  type: ToolType | null;
  t4c_model_id: number | null;
  git_model_id: number | null;
}

@Injectable({
  providedIn: 'root',
})
export class ModelService {
  base_url = new URL('projects/', environment.backend_url + '/');

  _model = new BehaviorSubject<Model | undefined>(undefined);
  _models = new BehaviorSubject<Model[] | undefined>(undefined);

  get model(): Model | undefined {
    return this._model.value;
  }
  get models(): Model[] | undefined {
    return this._models.value;
  }

  constructor(private http: HttpClient) {}

  list(project_slug: string): Observable<Model[]> {
    let url = new URL(`${project_slug}/models/`, this.base_url);
    return this.http.get<Model[]>(url.toString());
  }

  getModelBySlug(slug: string, project_slug: string): Observable<Model> {
    let url = new URL(`${project_slug}/models/${slug}/`, this.base_url);
    return this.http.get<Model>(url.toString());
  }

  createNewModel(project_slug: string, model: NewModel): Observable<Model> {
    let url = new URL(`${project_slug}/models`, this.base_url);
    return this.createModelGeneric(url, model);
  }

  setToolDetailsForModel(
    project_slug: string,
    model_slug: string,
    version_id: number,
    type_id: number
  ): Observable<Model> {
    let url = new URL(`${project_slug}/models/${model_slug}/`, this.base_url);
    return this.http.patch<Model>(url.toString(), { version_id, type_id });
  }

  createModelGeneric<T extends NewModel>(
    url: URL,
    new_model: T
  ): Observable<Model> {
    return this.http.post<Model>(url.toString(), new_model);
  }
}
