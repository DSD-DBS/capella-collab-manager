/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgIf, NgFor, NgClass, AsyncPipe, DatePipe } from '@angular/common';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButton, MatFabButton } from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatIcon } from '@angular/material/icon';
import { MatRadioGroup, MatRadioButton } from '@angular/material/radio';
import { MatTooltip } from '@angular/material/tooltip';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { filter, take } from 'rxjs';
import { Session, SessionsService } from 'src/app/openapi';
import { FullscreenService } from 'src/app/sessions/service/fullscreen.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';
import { FloatingWindowManagerComponent } from './floating-window-manager/floating-window-manager.component';
import { SessionViewerService } from './session-viewer.service';
import { TilingWindowManagerComponent } from './tiling-window-manager/tiling-window-manager.component';

@Component({
  selector: 'app-session',
  templateUrl: './session.component.html',
  styleUrls: ['./session.component.css'],
  standalone: true,
  imports: [
    NgIf,
    NgFor,
    NgxSkeletonLoaderModule,
    MatCheckbox,
    MatTooltip,
    FormsModule,
    MatRadioGroup,
    MatRadioButton,
    MatButton,
    MatIcon,
    NgClass,
    FloatingWindowManagerComponent,
    TilingWindowManagerComponent,
    MatFabButton,
    AsyncPipe,
    DatePipe,
  ],
})
@UntilDestroy()
export class SessionComponent implements OnInit, OnDestroy {
  cachedSessions?: CachedSession[] = undefined;

  selectedWindowType: string = 'floating';

  constructor(
    public userSessionService: UserSessionService,
    public sessionService: SessionService,
    private sessionsService: SessionsService,
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
      this.sessionsService
        .getSessionConnectionInformation(session.id)
        .subscribe((connectionInfo) => {
          this.sessionViewerService.pushSession(
            session,
            connectionInfo.payload,
          );
        });
    });
  }
}

type CachedSession = Session & {
  checked?: boolean;
};
