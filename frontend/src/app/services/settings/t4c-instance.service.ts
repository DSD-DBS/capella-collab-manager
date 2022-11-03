/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export type Protocol = 'tcp' | 'ssl' | 'ws' | 'wss';

export type BaseT4CInstance = {
  license: string;
  host: string;
  port: number;
  cdo_port: number;
  usage_api: string;
  rest_api: string;
  username: string;
  password: string;
  protocol: Protocol;
};

export type NewT4CInstance = BaseT4CInstance & {
  name: string;
  version_id: number;
};

export type T4CInstance = NewT4CInstance & {
  id: number;
  version: {
    id: number;
    name: string;
  };
};

@Injectable({
  providedIn: 'root',
})
export class T4CInstanceService {
  constructor(private http: HttpClient) {}

  base_url = `${environment.backend_url}/settings/modelsources/t4c/`;

  listInstances(): Observable<T4CInstance[]> {
    return this.http.get<T4CInstance[]>(this.base_url);
  }

  getInstance(id: number): Observable<T4CInstance> {
    return this.http.get<T4CInstance>(this.base_url + id);
  }

  createInstance(instance: NewT4CInstance): Observable<T4CInstance> {
    return this.http.post<T4CInstance>(this.base_url, instance);
  }

  updateInstance(
    id: number,
    instance: BaseT4CInstance
  ): Observable<T4CInstance> {
    return this.http.patch<T4CInstance>(this.base_url + id, instance);
  }
}
