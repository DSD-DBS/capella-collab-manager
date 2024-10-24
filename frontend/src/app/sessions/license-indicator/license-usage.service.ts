/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { SKIP_ERROR_HANDLING_CONTEXT } from '../../general/error-handling/error-handling.interceptor';
import {
  T4CLicenseServer,
  SettingsModelsourcesT4CLicenseServersService,
} from '../../openapi';

@Injectable({
  providedIn: 'root',
})
export class LicenseUsageWrapperService {
  private _licenseServerUsage = new BehaviorSubject<
    T4CLicenseServer[] | undefined
  >(undefined);

  readonly licenseServerUsage$ = this._licenseServerUsage.asObservable();

  constructor(
    private licenseServerService: SettingsModelsourcesT4CLicenseServersService,
  ) {
    this.loadLicenseServerUsage().subscribe();
  }

  loadLicenseServerUsage(): Observable<T4CLicenseServer[]> {
    return this.licenseServerService
      .getT4cLicenseServers(undefined, undefined, {
        context: SKIP_ERROR_HANDLING_CONTEXT,
      })
      .pipe(tap((usage) => this._licenseServerUsage.next(usage)));
  }
}
