/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ModelService } from 'src/app/projects/models/service/model.service';

@Injectable({
  providedIn: 'root',
})
export class ModelDiagramService {
  constructor(
    private http: HttpClient,
    private modelService: ModelService,
  ) {}

  getDiagramMetadata(
    projectSlug: string,
    modelSlug: string,
  ): Observable<DiagramCacheMetadata> {
    return this.http.get<DiagramCacheMetadata>(
      this.modelService.backendURLFactory(projectSlug, modelSlug) + '/diagrams',
    );
  }

  getDiagram(
    projectSlug: string,
    modelSlug: string,
    diagramUUID: string,
  ): Observable<Blob> {
    return this.http.get(
      this.modelService.backendURLFactory(projectSlug, modelSlug) +
        '/diagrams/' +
        diagramUUID,
      { responseType: 'blob' },
    );
  }
}

export type DiagramCacheMetadata = {
  diagrams: DiagramMetadata[];
  last_updated: string;
};

export type DiagramMetadata = {
  name: string;
  uuid: string;
  success: boolean;
};
