/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass, AsyncPipe } from '@angular/common';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule, MatFabButton } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { FullscreenService } from 'src/app/sessions/service/fullscreen.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { SessionViewerService } from './session-viewer.service';
import { TilingWindowManagerComponent } from './tiling-window-manager/tiling-window-manager.component';

@Component({
  selector: 'app-session-viewer',
  templateUrl: './session-viewer.component.html',
  imports: [
    NgxSkeletonLoaderModule,
    FormsModule,
    MatButtonModule,
    MatIconModule,
    NgClass,
    TilingWindowManagerComponent,
    MatFabButton,
    AsyncPipe,
    MatProgressSpinnerModule,
  ],
})
@UntilDestroy()
export class SessionViewerComponent implements OnInit, OnDestroy {
  constructor(
    public sessionService: SessionService,
    public sessionViewerService: SessionViewerService,
    public fullscreenService: FullscreenService,
    private route: ActivatedRoute,
  ) {
    this.fullscreenService.toggleFullscreen();
    this.fullscreenService.isFullscreen$
      .pipe(untilDestroyed(this))
      .subscribe(() => this.sessionViewerService.resizeSessions());
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      const sessionIDs = params['session-id'];
      if (typeof sessionIDs === 'string') {
        this.sessionViewerService.pushSession(sessionIDs);
      } else {
        for (const sessionID of sessionIDs) {
          this.sessionViewerService.pushSession(sessionID);
        }
      }
    });
  }

  ngOnDestroy(): void {
    this.sessionViewerService.clearSessions();
    this.fullscreenService.disableFullscreen();
  }
}
