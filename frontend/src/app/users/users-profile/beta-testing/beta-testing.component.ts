/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { map, take } from 'rxjs';
import { UsersService } from '../../../openapi';
import { UserWrapperService } from '../../user-wrapper/user-wrapper.service';

@Component({
  selector: 'app-beta-testing',
  imports: [MatButton, AsyncPipe, MatIcon],
  templateUrl: './beta-testing.component.html',
})
export class BetaTestingComponent {
  constructor(
    public userWrapperService: UserWrapperService,
    private usersService: UsersService,
  ) {}

  readonly isBetaTester$ = this.userWrapperService.user$.pipe(
    map((user) => user?.beta_tester ?? false),
  );

  setBetaTester(isBetaTester: boolean) {
    this.userWrapperService.user$.pipe(take(1)).subscribe((user) => {
      if (user) {
        this.usersService
          .updateUser(user.id, { beta_tester: isBetaTester })
          .subscribe(() => {
            this.userWrapperService.loadUser(user.id);
          });
      }
    });
  }
}
