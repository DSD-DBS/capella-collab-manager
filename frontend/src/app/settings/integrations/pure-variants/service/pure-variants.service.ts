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
export class PureVariantsService {
  baseUrl = environment.backend_url + '/settings/integrations/pure-variants';

  constructor(private http: HttpClient) {}

  getLicenseServerConfiguration(): Observable<PureVariantsConfiguration> {
    return this.http.get<PureVariantsConfiguration>(this.baseUrl);
  }

  setLicenseServerURL(value: string): Observable<PureVariantsConfiguration> {
    return this.http.patch<PureVariantsConfiguration>(this.baseUrl, {
      license_server_url: value,
    });
  }

  uploadLicenseServerFile(
    formData: FormData,
  ): Observable<PureVariantsConfiguration> {
    return this.http.post<PureVariantsConfiguration>(
      this.baseUrl + '/license-keys',
      formData,
    );
  }

  deleteLicenseServerFile(): Observable<PureVariantsConfiguration> {
    return this.http.delete<PureVariantsConfiguration>(
      this.baseUrl + '/license-keys/0',
    );
  }
}

export interface PureVariantsConfiguration {
  license_server_url?: string;
  license_key_filename: string;
}
