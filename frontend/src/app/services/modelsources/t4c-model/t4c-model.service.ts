/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, of } from 'rxjs';

export interface BaseT4CInstance {
  license: string;
  host: string;
  port: number;
  serverAPI: string;
  restAPI: string;
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
  constructor(http: HttpClient) {}

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
      serverAPI: 'api.com',
      restAPI: 'rest.com',
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
      serverAPI: 'api.com',
      restAPI: 'rest.com',
      username: 'me',
      password: 'pw',
    },
  };

  _instance = new BehaviorSubject<T4CInstance | undefined>(undefined);

  listInstances(): Observable<T4CInstance[]> {
    return of(Object.values(this.mock_instances) as T4CInstance[]);
  }

  getInstance(id: number): Observable<T4CInstance> {
    let instance = this.mock_instances[id];
    if (instance) return of(instance);
    throw Error('test');
  }

  createInstance(instance: NewT4CInstance): Observable<T4CInstance> {
    return of({
      id: 2,
      version: { id: instance.version_id, name: 'jspmdr' },
      ...instance,
    });
  }

  updateInstance(
    id: number,
    instance: BaseT4CInstance
  ): Observable<T4CInstance> {
    return of({
      id: 2,
      name: 'test',
      version_id: 2,
      version: { id: 2, name: 'jspmdr' },
      ...instance,
    });
  }
}
