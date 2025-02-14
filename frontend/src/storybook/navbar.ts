/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import { NavBarService } from '../app/general/nav-bar/nav-bar.service';
import { BadgeOutput } from '../app/openapi';

export class MockNavbarService implements Partial<NavBarService> {
  readonly logoUrl$ = new BehaviorSubject<string | undefined>(undefined);
  readonly badge$ = new BehaviorSubject<BadgeOutput | undefined>(undefined);
  readonly loaded$ = new BehaviorSubject<boolean>(true);

  constructor(
    logoUrl: string | undefined,
    badge: BadgeOutput | undefined,
    loaded: boolean,
  ) {
    this.logoUrl$.next(logoUrl);
    this.badge$.next(badge);
    this.loaded$.next(loaded);
  }
}

export const mockNavbarServiceProvider = (
  logoUrl: string | undefined,
  badge: BadgeOutput | undefined,
  loaded: boolean,
) => {
  return {
    provide: NavBarService,
    useValue: new MockNavbarService(logoUrl, badge, loaded),
  };
};
