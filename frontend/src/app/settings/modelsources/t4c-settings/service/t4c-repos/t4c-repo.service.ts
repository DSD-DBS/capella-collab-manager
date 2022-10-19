/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, map, Observable, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CRepoService {
  constructor(private http: HttpClient, private toastService: ToastService) {}

  _repositories = new BehaviorSubject<T4CServerRepository[]>([]);
  get repositories(): T4CServerRepository[] {
    return this._repositories.value;
  }

  urlFactory(instance_id: number): string {
    return `${environment.backend_url}/settings/modelsources/t4c/${instance_id}/repositories/`;
  }

  getT4CRepositories(instance_id: number): Observable<T4CServerRepository[]> {
    return this.http.get<T4CServerRepository[]>(this.urlFactory(instance_id));
  }

  createT4CRepository(
    instance_id: number,
    repository: CreateT4CRepository
  ): Observable<T4CRepository> {
    return this.http.post<T4CRepository>(
      this.urlFactory(instance_id),
      repository
    );
  }

  deleteRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    return this.http.delete<null>(
      `${this.urlFactory(instance_id)}${repository_id}/`
    );
  }

  startRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    return this.http.post<null>(
      `${this.urlFactory(instance_id)}${repository_id}/start/`,
      {}
    );
  }

  stopRepository(instance_id: number, repository_id: number): Observable<null> {
    return this.http.post<null>(
      `${this.urlFactory(instance_id)}${repository_id}/stop/`,
      {}
    );
  }

  recreateRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    return this.http.post<null>(
      `${this.urlFactory(instance_id)}${repository_id}/recreate/`,
      {}
    );
  }
}

export type CreateT4CRepository = {
  name: string;
};

export type T4CRepository = CreateT4CRepository & {
  id: number;
  instance: T4CInstance;
};

export type T4CServerRepository = T4CRepository & {
  status:
    | 'ONLINE'
    | 'OFFLINE'
    | 'INITIAL'
    | 'INSTANCE_UNREACHABLE'
    | 'NOT_FOUND'
    | 'LOADING';
};
