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
export class GuacamoleService {
  constructor(private http: HttpClient) {}

  getGucamoleToken(session_id: string): Observable<GuacamoleAuthentication> {
    return this.http.post<GuacamoleAuthentication>(
      environment.backend_url + '/sessions/' + session_id + '/guacamole-tokens',
      null,
    );
  }
}

export interface GuacamoleAuthentication {
  url: string;
  token: string;
}
