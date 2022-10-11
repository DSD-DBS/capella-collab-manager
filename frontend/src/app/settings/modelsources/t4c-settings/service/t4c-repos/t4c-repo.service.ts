/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, map, Observable, of, tap } from 'rxjs';
import { environment } from 'src/environments/environment';
import { ToastService } from '../../../../../helpers/toast/toast.service';

@Injectable({
  providedIn: 'root',
})
export class T4CRepoService {
  constructor(private http: HttpClient, private toastService: ToastService) {}
  base_url = new URL(
    'settings/modelsources/t4c/',
    environment.backend_url + '/'
  );

  _repositories = new BehaviorSubject<(T4CRepository & T4CServerRepository)[]>(
    []
  );
  get repositories(): (T4CRepository & T4CServerRepository)[] {
    return this._repositories.value;
  }

  url_factory(instance_id: number): URL {
    return new URL(`${instance_id}/repositories/`, this.base_url);
  }

  getT4CRepositories(instance_id: number): Observable<T4CServerRepository[]> {
    const url = this.url_factory(instance_id);
    return this.http.get<[T4CServerRepository[], boolean]>(url.toString()).pipe(
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
    return this.http.post<T4CRepository>(url.toString(), repository);
  }

  deleteRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    const url = new URL(`${repository_id}`, this.url_factory(instance_id));
    return this.http.delete<null>(url.toString());
  }

  startRepository(
    instance_id: number,
    repository_id: number
  ): Observable<null> {
    const url = new URL(
      `${repository_id}/start`,
      this.url_factory(instance_id)
    );
    return this.http.post<null>(url.toString(), {});
  }

  stopRepository(instance_id: number, repository_id: number): Observable<null> {
    const url = new URL(`${repository_id}/stop`, this.url_factory(instance_id));
    return this.http.post<null>(url.toString(), {});
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
  status?: 'ONLINE' | 'OFFLINE' | 'INSTANCE_UNREACHABLE';
};
