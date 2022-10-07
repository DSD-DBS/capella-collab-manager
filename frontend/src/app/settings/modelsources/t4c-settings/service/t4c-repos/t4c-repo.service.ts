/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CRepoService {
  constructor(private http: HttpClient) {}
  base_url = new URL(
    'settings/modelsources/t4c/',
    environment.backend_url + '/'
  );

  _repositories = new BehaviorSubject<T4CRepository[]>([]);
  get repositories(): T4CRepository[] {
    return this._repositories.value;
  }

  url_factory(instance_id: number): URL {
    return new URL(`${instance_id}/repositories/`, this.base_url);
  }

  getT4CRepositories(instance_id: number): Observable<Array<T4CRepository>> {
    const url = this.url_factory(instance_id);
    return this.http.get<T4CRepository[]>(url.toString());
  }

  createT4CRepository(
    instance_id: number,
    repository: CreateT4CRepository
  ): Observable<T4CRepository> {
    const url = this.url_factory(instance_id);
    return this.http.post<T4CRepository>(url.toString(), repository);
  }

  deleteRepository(
    instance_id: number,
    repository_id: number
  ): Observable<T4CRepository> {
    const url = new URL(`${repository_id}`, this.url_factory(instance_id));
    return this.http.delete<T4CRepository>(url.toString());
  }
}

export type CreateT4CRepository = {
  name: string;
};

export type T4CRepository = CreateT4CRepository & {
  id: number;
  instance_id: number;
};
