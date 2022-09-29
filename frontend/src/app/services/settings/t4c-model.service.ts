/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface BaseT4CInstance {
  license: string;
  host: string;
  port: number;
  usage_api: string;
  rest_api: string;
  username: string;
  password: string;
}

export interface NewT4CInstance extends BaseT4CInstance {
  name: string;
  version_id: number;
}

export interface T4CInstance extends NewT4CInstance {
  id: number;
  version: {
    id: number;
    name: string;
  };
}

@Injectable({
  providedIn: 'root',
})
export class T4CInstanceService {
  constructor(private http: HttpClient) {}

  base_url = new URL(
    'settings/modelsources/t4c/',
    environment.backend_url + '/'
  );

  mock_instances: { [id: number]: T4CInstance | undefined } = {
    0: {
      id: 0,
      name: 'Primary instance',
      version_id: 2,
      version: {
        id: 2,
        name: '6.0',
      },
      license: 'this-is-the-key',
      host: 'https://instance.com/example',
      port: 3000,
      usage_api: 'api.com',
      rest_api: 'rest.com',
      username: 'me',
      password: 'pw',
    },
    1: {
      id: 1,
      name: 'Secondary instance',
      version_id: 2,
      version: {
        id: 2,
        name: '6.0',
      },
      license: 'this-is-the-key',
      host: 'https://instance.com/example',
      port: 3000,
      usage_api: 'api.com',
      rest_api: 'rest.com',
      username: 'me',
      password: 'pw',
    },
  };

  _instance = new BehaviorSubject<T4CInstance | undefined>(undefined);

  listInstances(): Observable<T4CInstance[]> {
    return this.http.get<T4CInstance[]>(this.base_url.toString());
  }

  getInstance(id: number): Observable<T4CInstance> {
    const url = new URL(`${id}/`, this.base_url);
    return this.http.get<T4CInstance>(url.toString());
  }

  createInstance(instance: NewT4CInstance): Observable<T4CInstance> {
    return this.http.post<T4CInstance>(this.base_url.toString(), instance);
  }

  updateInstance(
    id: number,
    instance: BaseT4CInstance
  ): Observable<T4CInstance> {
    const url = new URL(`${id}/`, this.base_url);
    return this.http.patch<T4CInstance>(url.toString(), instance);
  }
}
