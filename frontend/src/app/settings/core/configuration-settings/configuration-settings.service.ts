/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

/* eslint-disable @typescript-eslint/no-explicit-any */
// We support any arbitrary configuration models, therefore, we have to use "any" here.
// The mapping to the correct model is done in the individual components.

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
