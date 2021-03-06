// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CSyncService {
  constructor(private http: HttpClient) {}

  syncRepositories(): Observable<void> {
    return this.http.post<void>(
      environment.backend_url + '/sync/repositories',
      null
    );
  }
}
