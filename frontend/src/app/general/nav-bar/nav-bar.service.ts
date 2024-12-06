/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { map } from 'rxjs';
import { BuiltInLinkItem, Role } from 'src/app/openapi';
import { environment } from 'src/environments/environment';
import { UnifiedConfigWrapperService } from '../../services/unified-config-wrapper/unified-config-wrapper.service';

@Injectable({
  providedIn: 'root',
})
export class NavBarService {
  constructor(
    private unifiedConfigWrapperService: UnifiedConfigWrapperService,
  ) {}

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
    prometheus: environment.prometheus_url,
    grafana: environment.grafana_url,
    smtp_mock: environment.smtp_mock_url,
    documentation: environment.docs_url + '/',
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
