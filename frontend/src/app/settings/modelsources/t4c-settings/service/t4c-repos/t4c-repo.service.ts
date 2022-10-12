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

  _repositories = new BehaviorSubject<(T4CRepository & T4CServerRepository)[]>(
    []
  );
  get repositories(): (T4CRepository & T4CServerRepository)[] {
    return this._repositories.value;
  }

  urlFactory(instance_id: number): string {
    return `${environment.backend_url}/settings/modelsources/t4c/${instance_id}/repositories/`;
  }

  getT4CRepositories(instance_id: number): Observable<T4CServerRepository[]> {
    const url = this.url_factory(instance_id);
    return this.http.get<[T4CServerRepository[], boolean]>(url).pipe(
      tap((res) => {
        if (!res[1]) {
          this.toastService.showError(
            'Instance Error',
            'The Instance is unreachable, check the REST API URL.'
          );
        }
      }),
      map((res) => res[0])
    );
  }

  createT4CRepository(
    instance_id: number,
    repository: CreateT4CRepository
  ): Observable<T4CRepository> {
    const url = this.url_factory(instance_id);
    return this.http.post<T4CRepository>(url, repository);
  }

  deleteRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    const url = `${this.urlFactory(instance_id)}${repository_id}/`;
    return this.http.delete<null>(url);
  }

  startRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    const url = `${this.urlFactory(instance_id)}${repository_id}/start/`;
    return this.http.post<null>(url, {});
  }

  stopRepository(instance_id: number, repository_id: number): Observable<null> {
    const url = `${this.urlFactory(instance_id)}${repository_id}/stop/`;
    return this.http.post<null>(url, {});
  }

  recreateRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    const url = `${this.urlFactory(instance_id)}${repository_id}/recreate/`;
    return this.http.post<null>(url, {});
  }
}

export type CreateT4CRepository = {
  name: string;
};

export type T4CRepository = CreateT4CRepository & {
  id: number;
  instance_id: number;
};

export type T4CServerRepository = T4CRepository & {
  status?: 'ONLINE' | 'OFFLINE' | 'INSTANCE_UNREACHABLE' | 'NOT_FOUND';
};
