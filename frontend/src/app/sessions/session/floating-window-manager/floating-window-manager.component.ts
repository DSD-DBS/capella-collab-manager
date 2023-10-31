/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, HostListener, Input, OnInit } from '@angular/core';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { Session } from 'src/app/schemes';
import { FullscreenService } from '../../service/fullscreen.service';

@Component({
  selector: 'app-floating-window-manager',
  templateUrl: './floating-window-manager.component.html',
  styleUrls: ['./floating-window-manager.component.css'],
})
@UntilDestroy()
export class FloatingWindowManagerComponent implements OnInit {
  @Input() sessions: Session[] = [];

  draggingActive = false;

  private debounceTimer?: number;

  constructor(public fullscreenService: FullscreenService) {}

  ngOnInit(): void {
    this.fullscreenService.isFullscreen$
      .pipe(untilDestroyed(this))
      .subscribe(() => this.resizeSessions());
  }

  focusSession(session: Session) {
    this.unfocusSession(session);

    document.getElementById('session-' + session.id)?.focus();
    session.focused = true;
  }

  unfocusSession(focusedSession: Session) {
    this.sessions
      .filter((session) => session !== focusedSession)
      .map((session) => (session.focused = false));
  }

  dragStart() {
    this.draggingActive = true;
  }

  dragStop() {
    this.draggingActive = false;
  }

  @HostListener('window:resize', ['$event'])
  onResize() {
    window.clearTimeout(this.debounceTimer);

    this.debounceTimer = window.setTimeout(() => {
      this.resizeSessions();
    }, 250);
  }

  resizeSessions() {
    Array.from(document.getElementsByTagName('iframe')).forEach((iframe) => {
      const session = this.sessions.find(
        (session) => 'session-' + session.id === iframe.id,
      );

      if (session?.reloadToResize) {
        this.reloadIFrame(iframe);
      }
    });
  }

  reloadIFrame(iframe: HTMLIFrameElement) {
    const src = iframe.src;

    iframe.removeAttribute('src');

    setTimeout(() => {
      iframe.src = src;
    }, 100);
  }
}
