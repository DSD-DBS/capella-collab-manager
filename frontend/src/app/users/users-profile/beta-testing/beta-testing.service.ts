/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { map } from 'rxjs';
import { OwnUserWrapperService } from '../../../services/user/user.service';

@Injectable({
  providedIn: 'root',
})
export class BetaTestingService {
  constructor(public userService: OwnUserWrapperService) {}

  readonly isBetaTester$ = this.userService.user$.pipe(
    map((user) => user?.beta_tester ?? false),
  );
}
