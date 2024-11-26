/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CdkCopyToClipboard } from '@angular/cdk/clipboard';
import { CdkDrag, CdkDragHandle } from '@angular/cdk/drag-drop';
import { NgClass, AsyncPipe } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { MatTooltip } from '@angular/material/tooltip';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { debounceTime, fromEvent } from 'rxjs';
import { ToastService } from '../../../helpers/toast/toast.service';
import { SessionIFrameComponent } from '../session-iframe/session-iframe.component';
import { SessionViewerService, ViewerSession } from '../session-viewer.service';

@Component({
  selector: 'app-floating-window-manager',
  templateUrl: './floating-window-manager.component.html',
  standalone: true,
  imports: [
    CdkDrag,
    NgClass,
    CdkDragHandle,
    MatIcon,
    SessionIFrameComponent,
    AsyncPipe,
    MatTooltip,
    CdkCopyToClipboard,
  ],
})
@UntilDestroy()
export class FloatingWindowManagerComponent implements OnInit {
  constructor(
    public sessionViewerService: SessionViewerService,
    public toastService: ToastService,
  ) {}

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
