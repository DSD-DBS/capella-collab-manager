/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { inject } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  CanActivateFn,
  RouterStateSnapshot,
} from '@angular/router';
import { AuthenticationWrapperService } from 'src/app/services/auth/auth.service';

export const authGuard: CanActivateFn = (
  _route: ActivatedRouteSnapshot,
  _state: RouterStateSnapshot,
) => {
  const authService = inject(AuthenticationWrapperService);

  if (authService.isLoggedIn()) {
    return true;
  } else {
    // Needs window.location, since Router.url isn't updated yet
    authService.redirectURL = window.location.pathname + window.location.search;
    authService.login();
    return false;
  }
};
