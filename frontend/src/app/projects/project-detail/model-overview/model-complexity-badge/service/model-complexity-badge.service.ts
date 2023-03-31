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
export class ModelComplexityBadgeService {
  constructor(private http: HttpClient, private modelService: ModelService) {}

  getModelComplexityBadge(
    projectSlug: string,
    modelSlug: string
  ): Observable<Blob> {
    return this.http.get(
      this.modelService.backendURLFactory(projectSlug, modelSlug) +
        '/badges/complexity',
      {
        responseType: 'blob',
        headers: {
          'Skip-Frontend-Error-Handling': 'true',
        },
      }
    );
  }
}
