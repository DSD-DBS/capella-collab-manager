/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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
