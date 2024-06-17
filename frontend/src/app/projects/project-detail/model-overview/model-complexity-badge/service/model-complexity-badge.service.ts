/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpContext } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { SKIP_ERROR_HANDLING } from 'src/app/general/error-handling/error-handling.interceptor';
import { ProjectsModelsService } from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class ModelComplexityBadgeService {
  constructor(private projectModelService: ProjectsModelsService) {}

  getModelComplexityBadge(
    projectSlug: string,
    modelSlug: string,
  ): Observable<Blob> {
    return this.projectModelService.getModelComplexityBadge(
      projectSlug,
      modelSlug,
      undefined,
      undefined,
      {
        context: new HttpContext().set(SKIP_ERROR_HANDLING, true),
      },
    );
  }
}
