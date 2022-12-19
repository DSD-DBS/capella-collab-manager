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
export class PureVariantsService {
  baseUrl = environment.backend_url + '/settings/integrations/pure-variants';

  constructor(private http: HttpClient) {}

  getLicenseServerURL(): Observable<PureVariantsConfiguration> {
    return this.http.get<PureVariantsConfiguration>(this.baseUrl);
  }

  setLicenseServerURL(value: string): Observable<PureVariantsConfiguration> {
    return this.http.patch<PureVariantsConfiguration>(this.baseUrl, {
      license_server_url: value,
    });
  }
}

export type PureVariantsConfiguration = {
  license_server_url?: string;
};
