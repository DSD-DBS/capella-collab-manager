/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
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
  base_url = environment.backend_url + '/projects/';

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
    return this.http.get<Model[]>(`${this.base_url}${project_slug}/models/`);
  }

  getModelBySlug(slug: string, project_slug: string): Observable<Model> {
    return this.http.get<Model>(
      `${this.base_url}${project_slug}/models/${slug}/`
    );
  }

  createNewModel(project_slug: string, model: NewModel): Observable<Model> {
    return this.http.post<Model>(
      `${this.base_url}${project_slug}/models`,
      model
    );
  }

  setToolDetailsForModel(
    project_slug: string,
    model_slug: string,
    version_id: number,
    type_id: number
  ): Observable<Model> {
    return this.http.patch<Model>(
      `${this.base_url}${project_slug}/models/${model_slug}/`,
      { version_id, type_id }
    );
  }
}
