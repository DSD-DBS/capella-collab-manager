/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PureVariantService {
  baseUrl = environment.backend_url + '/settings/integrations/pure-variant/';

  constructor(private http: HttpClient) {}

  get_license(): Observable<{ value: string } | null> {
    return this.http.get<{ value: string } | null>(this.baseUrl);
  }

  set_license(value: string): Observable<{ value: string }> {
    return this.http.patch<{ value: string }>(this.baseUrl, {
      value,
    });
  }
}
