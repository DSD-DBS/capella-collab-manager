/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { delay, expand, of } from 'rxjs';
import { UserSessionService } from '../service/user-session.service';

@UntilDestroy()
@Component({
  selector: 'app-user-sessions-wrapper',
  templateUrl: './user-sessions-wrapper.component.html',
  styleUrls: ['./user-sessions-wrapper.component.css'],
  standalone: true,
})
export class UserSessionsWrapperComponent implements OnInit {
  constructor(private userSessionService: UserSessionService) {}

  ngOnInit(): void {
    of(undefined)
      .pipe(
        expand(() =>
          this.userSessionService
            .loadSessionsObservable()
            .pipe(delay(2000), untilDestroyed(this)),
        ),
      )
      .subscribe();
  }
}
