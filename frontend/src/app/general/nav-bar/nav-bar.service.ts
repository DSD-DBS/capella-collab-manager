/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { map } from 'rxjs';
import {
  DOCS_URL,
  GRAFANA_URL,
  PROMETHEUS_URL,
  SMTP_MOCK_URL,
} from 'src/app/environment';
import { BuiltInLinkItem, Role } from 'src/app/openapi';
import { UnifiedConfigWrapperService } from 'src/app/services/unified-config-wrapper/unified-config-wrapper.service';

@Injectable({
  providedIn: 'root',
})
export class NavBarService {
  private unifiedConfigWrapperService = inject(UnifiedConfigWrapperService);

  readonly navbarItems$ = this.unifiedConfigWrapperService.unifiedConfig$.pipe(
    map(
      (unifiedConfig): NavBarItem[] =>
        unifiedConfig?.navbar?.external_links.map((link) => ({
          name: link.name,
          href: link.service ? this._linkMap[link.service] : link.href,
          target: '_blank',
          icon: 'open_in_new',
          requiredRole: link.role,
        })) || [],
    ),
    map((items) => [...this.internalNavbarItems, ...items]),
  );

  readonly logoUrl$ = this.unifiedConfigWrapperService.unifiedConfig$.pipe(
    map((unifiedConfig) => unifiedConfig?.navbar?.logo_url),
  );

  readonly loaded$ = this.unifiedConfigWrapperService.unifiedConfig$.pipe(
    map((unifiedConfig) => !!unifiedConfig),
  );

  readonly badge$ = this.unifiedConfigWrapperService.unifiedConfig$.pipe(
    map((unifiedConfig) => unifiedConfig?.navbar?.badge),
  );
  sidenav?: MatSidenav;
  toggle(): void {
    this.sidenav?.toggle();
  }

  private internalNavbarItems: NavBarItem[] = [
    {
      name: 'Projects',
      routerLink: '/projects',
      requiredRole: 'user',
    },
    {
      name: 'Sessions',
      routerLink: '',
      requiredRole: 'user',
    },
    {
      name: 'Session overview',
      routerLink: ['/sessions', 'overview'],
      requiredRole: 'administrator',
    },
  ];

  private _linkMap: Record<BuiltInLinkItem, string> = {
    prometheus: PROMETHEUS_URL,
    grafana: GRAFANA_URL,
    smtp_mock: SMTP_MOCK_URL,
    documentation: DOCS_URL + '/',
  };
}

export interface NavBarItem {
  name: string;
  routerLink?: string | string[];
  href?: string;
  target?: string;
  requiredRole: Role;
  icon?: string;
}
