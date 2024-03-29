/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit, OnDestroy } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, take } from 'rxjs';
import { FullscreenService } from 'src/app/sessions/service/fullscreen.service';
import {
  Session,
  SessionService,
} from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';
import { SessionViewerService } from './session-viewer.service';

@Component({
  selector: 'app-session',
  templateUrl: './session.component.html',
  styleUrls: ['./session.component.css'],
})
@UntilDestroy()
export class SessionComponent implements OnInit, OnDestroy {
  cachedSessions?: CachedSession[] = undefined;

  selectedWindowType: string = 'floating';

  constructor(
    public userSessionService: UserSessionService,
    public sessionService: SessionService,
    public sessionViewerService: SessionViewerService,
    public fullscreenService: FullscreenService,
  ) {
    this.userSessionService.loadSessions();

    this.fullscreenService.isFullscreen$
      .pipe(untilDestroyed(this))
      .subscribe(() => this.sessionViewerService.resizeSessions());
  }

  get checkedSessions(): undefined | CachedSession[] {
    return this.cachedSessions?.filter((session) => session.checked);
  }

  get isTilingWindowManager(): boolean {
    return this.selectedWindowType === 'tiling';
  }

  get isFloatingWindowManager(): boolean {
    return this.selectedWindowType === 'floating';
  }

  ngOnInit(): void {
    this.initializeCachedSessions();
  }

  ngOnDestroy(): void {
    this.sessionViewerService.clearSessions();
  }

  initializeCachedSessions() {
    this.userSessionService.sessions$
      .pipe(
        filter((sessions) => sessions !== undefined),
        take(1),
      )
      .subscribe((sessions) => {
        this.cachedSessions = sessions?.map((session) => {
          (session as CachedSession).checked = false;
          return session;
        });
      });
  }

  selectSessions() {
    this.checkedSessions?.forEach((session) => {
      this.sessionService
        .getSessionConnectionInformation(session.id)
        .subscribe((connectionInfo) => {
          this.sessionViewerService.pushSession(session, connectionInfo);
        });
    });
  }
}

type CachedSession = Session & {
  checked?: boolean;
};
