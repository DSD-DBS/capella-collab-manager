/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subscription, tap, timer } from 'rxjs';
import { UserSessionService } from '../service/user-session.service';

@Component({
  selector: 'app-user-sessions-wrapper',
  templateUrl: './user-sessions-wrapper.component.html',
  styleUrls: ['./user-sessions-wrapper.component.css'],
})
export class UserSessionsWrapperComponent implements OnInit, OnDestroy {
  constructor(private userSessionService: UserSessionService) {}

  private refreshSessionsSubscription?: Subscription;

  ngOnInit(): void {
    this.refreshSessionsSubscription = timer(0, 2000)
      .pipe(tap(() => this.userSessionService.loadSessions()))
      .subscribe();
  }

  ngOnDestroy(): void {
    this.refreshSessionsSubscription?.unsubscribe();
  }
}
