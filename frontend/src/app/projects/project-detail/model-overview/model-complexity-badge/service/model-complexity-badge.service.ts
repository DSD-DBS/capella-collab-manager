/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient, HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { SKIP_ERROR_HANDLING } from 'src/app/general/error-handling/error-handling.interceptor';
import { ModelService } from 'src/app/projects/models/service/model.service';

@Injectable({
  providedIn: 'root',
})
export class ModelComplexityBadgeService {
  constructor(
    private http: HttpClient,
    private modelService: ModelService,
  ) {}

  getModelComplexityBadge(
    projectSlug: string,
    modelSlug: string,
  ): Observable<Blob> {
    return this.http.get(
      this.modelService.backendURLFactory(projectSlug, modelSlug) +
        '/badges/complexity',
      {
        responseType: 'blob',
        context: new HttpContext().set(SKIP_ERROR_HANDLING, true),
      },
    );
  }
}
