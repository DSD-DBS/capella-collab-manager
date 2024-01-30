/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class PolarionInstanceService {
  private BACKEND_URL_PREFIX =
    environment.backend_url + '/settings/modelsources/polarion';

  private _polarionInstances = new BehaviorSubject<
    PolarionInstance[] | undefined
  >(undefined);
  private _polarionInstance = new BehaviorSubject<PolarionInstance | undefined>(
    undefined,
  );
  public readonly polarionInstances$ = this._polarionInstances.asObservable();
  public readonly polarionInstance$ = this._polarionInstance.asObservable();

  constructor(private http: HttpClient) {}

  loadPolarionInstances(): void {
    this.http.get<PolarionInstance[]>(this.BACKEND_URL_PREFIX).subscribe({
      next: (polarionInstance) =>
        this._polarionInstances.next(polarionInstance),
      error: () => this._polarionInstances.next(undefined),
    });
  }

  createPolarionInstance(
    polarionInstance: PolarionInstance,
  ): Observable<PolarionInstance> {
    return this.http
      .post<PolarionInstance>(this.BACKEND_URL_PREFIX, {
        name: polarionInstance.name,
        url: polarionInstance.url,
      })
      .pipe(tap(() => this.loadPolarionInstances()));
  }
}

export type PolarionInstance = {
  id: number;
  name: string;
  url: string;
};
