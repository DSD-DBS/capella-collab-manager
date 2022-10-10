/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { T4CRepository } from '../../settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

export type T4CServerRepository = {
  name: string;
  status?: 'ONLINE' | 'OFFLINE' | 'NOT FOUND';
};

@Injectable({
  providedIn: 'root',
})
export class T4CSyncService {
  constructor(private http: HttpClient) {}

  base_url = new URL(
    'settings/modelsources/t4c/',
    environment.backend_url + '/'
  );

  url_factory(instance_id: number): URL {
    return new URL(`${instance_id}/sync/`, this.base_url);
  }

  syncRepositories(instance_id: number): Observable<T4CServerRepository[]> {
    return this.http.get<T4CServerRepository[]>(
      this.url_factory(instance_id).toString()
    );
  }

  createRepository(
    instance_id: number,
    name: string
  ): Observable<T4CServerRepository> {
    return this.http.post<T4CServerRepository>(
      this.url_factory(instance_id).toString(),
      { name }
    );
  }
}
