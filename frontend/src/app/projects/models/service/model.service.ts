/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ModelRestrictions } from 'src/app/projects/models/model-restrictions/service/model-restrictions.service';
import { T4CModel } from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { GetGitModel } from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import {
  Tool,
  ToolNature,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';
import { environment } from 'src/environments/environment';

export type NewModel = {
  name: string;
  description: string;
  tool_id: number;
};

export type Model = {
  id: number;
  project_slug: string;
  slug: string;
  name: string;
  description: string;
  tool: Tool;
  version?: ToolVersion;
  nature?: ToolNature;
  t4c_models: T4CModel[];
  git_models: GetGitModel[];
  restrictions: ModelRestrictions;
};

export type PatchModel = {
  description?: string;
  nature_id?: number;
  version_id?: number;
};

@Injectable({
  providedIn: 'root',
})
export class ModelService {
  base_url = environment.backend_url + '/projects/';

  _model = new BehaviorSubject<Model | undefined>(undefined);
  _models = new BehaviorSubject<Model[] | undefined>(undefined);

  backendURLFactory(projectSlug: string, modelSlug: string) {
    return `${this.base_url}${projectSlug}/models/${modelSlug}`;
  }

  get model(): Model | undefined {
    return this._model.value;
  }

  get models(): Model[] | undefined {
    return this._models.value;
  }

  constructor(private http: HttpClient) {}

  getModels(project_slug: string): Observable<Model[]> {
    return this.http.get<Model[]>(`${this.base_url}${project_slug}/models`);
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

  deleteModel(project_slug: string, model: Model): Observable<void> {
    return this.http.delete<void>(
      `${this.base_url}${project_slug}/models/${model.slug}`
    );
  }

  setToolDetailsForModel(
    project_slug: string,
    model_slug: string,
    version_id: number,
    nature_id: number
  ): Observable<Model> {
    return this.http.patch<Model>(
      `${this.base_url}${project_slug}/models/${model_slug}/`,
      { version_id, nature_id }
    );
  }

  updateModelDescription(
    project_slug: string,
    model_slug: string,
    patchModel: PatchModel
  ): Observable<Model> {
    return this.http.patch<Model>(
      `${this.base_url}${project_slug}/models/${model_slug}/`,
      patchModel
    );
  }
}
