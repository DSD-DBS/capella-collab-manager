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
    // Construct the breadcrumb hierarchy
    const root = router.routerState.snapshot.root;
    const breadcrumbs: Breadcrumb[] = [];
    this.addBreadcrumb(root, [], breadcrumbs);

    // Emit the new hierarchy
    this._breadcrumbs.next(breadcrumbs);
  }

  private addBreadcrumb(
    route: ActivatedRouteSnapshot | null,
    parentUrl: string[],
    breadcrumbs: Breadcrumb[]
  ) {
    if (route) {
      const routeUrl = parentUrl.concat(route.url.map((url) => url.path));

      if (route.data.breadcrumb) {
        const breadcrumb = {
          label: expand(route.data.breadcrumb, this.placeholders),
          url: route.data.redirect
            ? expand(route.data.redirect, this.placeholders)
            : '/' + routeUrl.join('/'),
        };
        breadcrumbs.push(breadcrumb);
      }

      this.addBreadcrumb(route.firstChild, routeUrl, breadcrumbs);
    }
  }
}

const expand = (term: string | Function, placeholders: Data) => {
  // The breadcrumb can be defined as a static string or as a function to construct the breadcrumb element out of the route data
  return typeof term === 'function' ? term(placeholders) || '...' : term;
};
