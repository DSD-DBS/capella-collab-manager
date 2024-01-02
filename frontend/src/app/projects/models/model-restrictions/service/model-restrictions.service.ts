/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ModelRestrictionsService {
  constructor(private http: HttpClient) {}

  patchModelRestrictions(
    projectSlug: string,
    modelSlug: string,
    modelRestrictions: ModelRestrictions,
  ): Observable<ModelRestrictions> {
    return this.http.patch<ModelRestrictions>(
      `${environment.backend_url}/projects/${projectSlug}/models/${modelSlug}/restrictions`,
      modelRestrictions,
    );
  }
}

export function areRestrictionsEqual(
  a: ModelRestrictions,
  b: ModelRestrictions,
): boolean {
  return a.allow_pure_variants === b.allow_pure_variants;
}

export type ModelRestrictions = {
  allow_pure_variants: boolean;
};
