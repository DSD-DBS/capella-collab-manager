/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  Data,
  NavigationEnd,
  Router,
} from '@angular/router';
import { BehaviorSubject } from 'rxjs';
import { filter } from 'rxjs/operators';

export interface Breadcrumb {
  label: string;
  url: string;
}

@Injectable({
  providedIn: 'root',
})
export class BreadcrumbsService {
  private readonly _breadcrumbs = new BehaviorSubject<Breadcrumb[]>([]);

  readonly breadcrumbs = this._breadcrumbs.asObservable();
  private placeholders: Data = {};

  constructor(private router: Router) {
    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe(() => this.updateBreadcrumbs(router));
  }

  public updatePlaceholder(placeholders: Data) {
    this.placeholders = {
      ...this.placeholders,
      ...placeholders,
    };
    this.updateBreadcrumbs(this.router);
  }

  private updateBreadcrumbs(router: Router) {
    const root = router.routerState.snapshot.root;
    this._breadcrumbs.next(breadcrumbs(root, this.placeholders));
  }
}

const breadcrumbs = (
  route: ActivatedRouteSnapshot | null,
  placeholders: Data,
  parentUrl?: string[]
): Breadcrumb[] => {
  if (!route) {
    return [];
  }

  const routeUrl = (parentUrl || []).concat(route.url.map((url) => url.path));

  if (route.data.breadcrumb) {
    const breadcrumb = {
      label: expand(route.data.breadcrumb, placeholders),
      url: route.data.redirect
        ? expand(route.data.redirect, placeholders)
        : '/' + routeUrl.join('/'),
    };
    return [breadcrumb].concat(
      breadcrumbs(route.firstChild, placeholders, routeUrl)
    );
  }

  return breadcrumbs(route.firstChild, placeholders, routeUrl);
};

const expand = (term: string | Function, placeholders: Data) => {
  return typeof term === 'function' ? term(placeholders) || '...' : term;
};
