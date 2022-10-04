/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { environment } from '../../../environments/environment';

export type BaseT4CInstance = {
  license: string;
  host: string;
  port: number;
  usage_api: string;
  rest_api: string;
  username: string;
  password: string;
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

  base_url = new URL(
    'settings/modelsources/t4c/',
    environment.backend_url + '/'
  );

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
