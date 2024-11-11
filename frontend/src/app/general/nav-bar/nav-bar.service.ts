/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { BehaviorSubject, map, Observable, tap } from 'rxjs';
import {
  BuiltInLinkItem,
  NavbarConfigurationOutput,
  NavbarService as OpenAPINavbarService,
  Role,
} from 'src/app/openapi';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class NavBarService {
  constructor(private navbarService: OpenAPINavbarService) {
    this.loadNavbarConfig().subscribe();
  }

  loadNavbarConfig(): Observable<NavbarConfigurationOutput> {
    return this.navbarService
      .getNavbar()
      .pipe(tap((navConf) => this._navbarConfig.next(navConf)));
  }

  private _navbarConfig = new BehaviorSubject<
    NavbarConfigurationOutput | undefined
  >(undefined);

  readonly navbarItems$ = this._navbarConfig.pipe(
    map(
      (navbarConfig): NavBarItem[] =>
        navbarConfig?.external_links.map((link) => ({
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
