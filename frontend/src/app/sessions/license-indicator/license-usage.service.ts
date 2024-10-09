/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import {
  PublicLicenseServerWithUsage,
  SettingsModelsourcesT4CLicenseServersService,
} from '../../openapi';

@Injectable({
  providedIn: 'root',
})
export class LicenseUsageWrapperService {
  private _licenseServerUsage = new BehaviorSubject<
    PublicLicenseServerWithUsage[] | undefined
  >(undefined);

  readonly licenseServerUsage$ = this._licenseServerUsage.asObservable();

  constructor(
    private licenseServerService: SettingsModelsourcesT4CLicenseServersService,
  ) {
    this.loadLicenseServerUsage().subscribe();
  }

  loadLicenseServerUsage(): Observable<PublicLicenseServerWithUsage[]> {
    return this.licenseServerService
      .getT4cLicenseServersUsage()
      .pipe(tap((usage) => this._licenseServerUsage.next(usage)));
  }
}
