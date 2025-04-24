/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import {
  NavBarItem,
  NavBarService,
} from '../app/general/nav-bar/nav-bar.service';
import { BadgeOutput } from '../app/openapi';

export const mockBadge: Readonly<BadgeOutput> = {
  variant: 'warning',
  text: 'Storybook',
  show: true,
};

export const mockNavbarItems: NavBarItem[] = [
  {
    name: 'Projects',
    requiredRole: 'user',
  },
  {
    name: 'Sessions',
    requiredRole: 'user',
  },
  {
    name: 'Session overview',
    requiredRole: 'administrator',
  },
  {
    name: 'Prometheus',
    requiredRole: 'administrator',
    icon: 'open_in_new',
    href: '#',
  },
  {
    name: 'Grafana',
    requiredRole: 'administrator',
    icon: 'open_in_new',
    href: '#',
  },
  {
    name: 'Documentation',
    requiredRole: 'user',
    icon: 'open_in_new',
    href: '#',
  },
];

export class MockNavbarService implements Partial<NavBarService> {
  readonly navbarItems$ = new BehaviorSubject<NavBarItem[]>([]);
  readonly logoUrl$ = new BehaviorSubject<string | undefined>(undefined);
  readonly badge$ = new BehaviorSubject<BadgeOutput | undefined>(undefined);
  readonly loaded$ = new BehaviorSubject<boolean>(true);

  constructor(
    navbarItems: NavBarItem[],
    logoUrl: string | undefined = undefined,
    badge: BadgeOutput | undefined = undefined,
    loaded = true,
  ) {
    this.navbarItems$.next(navbarItems);
    this.logoUrl$.next(logoUrl);
    this.badge$.next(badge);
    this.loaded$.next(loaded);
  }
}

export const mockNavbarServiceProvider = (
  navbarItems: NavBarItem[],
  logoUrl: string | undefined,
  badge: BadgeOutput | undefined,
  loaded: boolean,
) => {
  return {
    provide: NavBarService,
    useValue: new MockNavbarService(navbarItems, logoUrl, badge, loaded),
  };
};
