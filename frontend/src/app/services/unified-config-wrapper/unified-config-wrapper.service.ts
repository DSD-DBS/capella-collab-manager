/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { UnifiedConfig, ConfigurationService } from '../../openapi';

@Injectable({
  providedIn: 'root',
})
export class UnifiedConfigWrapperService {
  constructor(private configurationService: ConfigurationService) {
    this.loadUnifiedConfig().subscribe();
  }

  loadUnifiedConfig(): Observable<UnifiedConfig> {
    return this.configurationService
      .getUnifiedConfig()
      .pipe(tap((unified) => this._unifiedConfig.next(unified)));
  }
  private _unifiedConfig = new BehaviorSubject<UnifiedConfig | undefined>(
    undefined,
  );

  get unifiedConfig() {
    return this._unifiedConfig.value;
  }

  readonly unifiedConfig$ = this._unifiedConfig.asObservable();
}
