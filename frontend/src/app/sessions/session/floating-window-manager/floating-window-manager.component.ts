/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { debounceTime, fromEvent } from 'rxjs';
import { SessionViewerService, ViewerSession } from '../session-viewer.service';

@Component({
  selector: 'app-floating-window-manager',
  templateUrl: './floating-window-manager.component.html',
})
@UntilDestroy()
export class FloatingWindowManagerComponent implements OnInit {
  constructor(public sessionViewerService: SessionViewerService) {}

  ngOnInit(): void {
    fromEvent(window, 'resize')
      .pipe(untilDestroyed(this), debounceTime(250))
      .subscribe(() => this.sessionViewerService.resizeSessions());
  }

  dragStart(): void {
    this.sessionViewerService.disableAllSessions();
  }

  dragStop(): void {
    this.sessionViewerService.enableAllSessions();
  }

  trackBySessionId(_: number, session: ViewerSession): string {
    return session.id;
  }
}
