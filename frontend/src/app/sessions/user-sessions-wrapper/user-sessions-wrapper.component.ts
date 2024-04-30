/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { tap, timer } from 'rxjs';
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
    timer(0, 2000)
      .pipe(
        untilDestroyed(this),
        tap(() => this.userSessionService.loadSessions()),
      )
      .subscribe();
  }
}
