/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { map } from 'rxjs';
import { UnifiedConfigWrapperService } from '../../services/unified-config-wrapper/unified-config-wrapper.service';

@Injectable({
  providedIn: 'root',
})
export class MetadataService {
  constructor(
    private unifiedConfigWrapperService: UnifiedConfigWrapperService,
  ) {}

  readonly backendMetadata =
    this.unifiedConfigWrapperService.unifiedConfig$.pipe(
      map((unifiedConfig) => unifiedConfig?.metadata),
    );
}
