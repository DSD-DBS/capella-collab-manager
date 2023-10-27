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
export class ConfigurationSettingsService {
  BACKEND_URL_PREFIX = environment.backend_url + '/settings/configurations';

  constructor(private http: HttpClient) {}

  getConfigurationSettings(name: string): Observable<any> {
    return this.http.get<any>(this.BACKEND_URL_PREFIX + '/' + name);
  }

  putConfigurationSettings(name: string, value: any): Observable<any> {
    return this.http.put<any>(this.BACKEND_URL_PREFIX + '/' + name, value);
  }
}
