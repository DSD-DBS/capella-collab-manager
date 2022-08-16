// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class T4CRepoService {
  constructor(private http: HttpClient) {}
  repositories: Array<T4CRepository> = [];

  getT4CRepositories(instance_id: number): Observable<Array<T4CRepository>> {
    return this.http
      .get<Array<T4CRepository>>(
        `${environment.backend_url}/integrations/modelsources/t4c/instances/${instance_id}/repositories`
      )
      .pipe(
        tap((res: Array<T4CRepository>) => {
          this.repositories = res;
        })
      );
  }

  createT4CRepository(
    name: string,
    instance_id: number
  ): Observable<T4CRepository> {
    return this.http.post<T4CRepository>(
      `${environment.backend_url}/integrations/modelsources/t4c/instances/${instance_id}/repositories`,
      { name: name }
    );
  }

  deleteRepository(
    instance_id: number,
    repository_name: string
  ): Observable<T4CRepository> {
    return this.http.delete<T4CRepository>(
      `${environment.backend_url}/integrations/modelsources/t4c/instances/${instance_id}/repositories/${repository_name}`
    );
  }
}

export interface T4CRepository {
  id: number;
  name: string;
  instance_id: number;
}
