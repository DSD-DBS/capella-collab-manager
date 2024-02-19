/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { MatSidenav } from '@angular/material/sidenav';
import { UserRole } from 'src/app/services/user/user.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class NavBarService {
  sidenav?: MatSidenav;

  toggle(): void {
    this.sidenav?.toggle();
  }

  navBarItems: NavBarItem[] = [
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
      name: 'Session viewer',
      routerLink: ['/session'],
      requiredRole: 'user',
    },
    {
      name: 'Session overview',
      routerLink: ['/sessions', 'overview'],
      requiredRole: 'administrator',
    },
    {
      name: 'Prometheus',
      href: environment.prometheus_url,
      target: '_blank',
      icon: 'open_in_new',
      requiredRole: 'administrator',
    },
    {
      name: 'Grafana',
      href: environment.grafana_url,
      target: '_blank',
      icon: 'open_in_new',
      requiredRole: 'administrator',
    },
    {
      name: 'Documentation',
      href: environment.docs_url,
      target: '_blank',
      icon: 'open_in_new',
      requiredRole: 'user',
    },
  ];
}

export type NavBarItem = {
  name: string;
  routerLink?: string | string[];
  href?: string;
  target?: string;
  requiredRole: UserRole;
  icon?: string;
};
