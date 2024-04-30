/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgFor, NgIf, NgClass } from '@angular/common';
import { Component, HostListener, OnInit } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter } from 'rxjs';
import { SessionIFrameComponent } from '../session-iframe/session-iframe.component';
import { SessionViewerService, ViewerSession } from '../session-viewer.service';

@Component({
  selector: 'app-tiling-window-manager',
  templateUrl: './tiling-window-manager.component.html',
  standalone: true,
  imports: [NgFor, NgIf, MatIcon, SessionIFrameComponent, NgClass],
})
@UntilDestroy()
export class TilingWindowManagerComponent implements OnInit {
  private _tilingSessions: TilingSession[] = [];

  get sessions(): TilingSession[] {
    return this._tilingSessions.sort((a, b) => a.index - b.index);
  }

  public resizeState: ResizeState = {};

  private minimumSessionWidth = 0;

  constructor(public sessionViewerService: SessionViewerService) {}

  ngOnInit(): void {
    this.sessionViewerService.sessions$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((viewerSessions) => {
        const sessionMap = new Map(viewerSessions.map((s) => [s.id, s]));

        const hasSessionDifference =
          this._tilingSessions.length !== viewerSessions.length ||
          viewerSessions.some(
            (session) =>
              !this._tilingSessions.some((ts) => ts.id === session.id),
          );

        if (hasSessionDifference) {
          this._tilingSessions = viewerSessions.map((session, index) => ({
            ...session,
            index: index,
            width: -1,
            fullscreen: false,
          }));
          this.resetWidths();
        } else {
          this._tilingSessions = this._tilingSessions.map((tilingSession) => {
            const sessionUpdate = sessionMap.get(tilingSession.id);
            return sessionUpdate
              ? { ...tilingSession, ...sessionUpdate }
              : tilingSession;
          });
        }
      });
  }

  onMouseDown(event: MouseEvent, index: number): void {
    this.sessionViewerService.disableAllSessions();
    const leftSession = this.getSessionByIndex(index);
    const rightSession = this.getSessionByIndex(index + 1);

    if (leftSession && rightSession) {
      this.resizeState = {
        index: index,
        startX: event.clientX,
        leftSession: leftSession,
        rightSession: rightSession,
        startWidthLeft: leftSession.width,
        startWidthRight: rightSession.width,
      };
    }
  }

  @HostListener('window:mousemove', ['$event'])
  onMouseMove(event: MouseEvent): void {
    if (this.isValidResizeState(this.resizeState)) {
      const delta = event.clientX - this.resizeState.startX;
      const [newWidthLeft, newWidthRight] = this.calculateNewWidths(
        this.resizeState,
        delta,
      );

      this.resizeState.leftSession.width = newWidthLeft;
      this.resizeState.rightSession.width = newWidthRight;
    }
  }

  @HostListener('window:mouseup')
  onMouseUp(): void {
    if (this.isValidResizeState(this.resizeState)) {
      // Only trigger if resize is active
      this.sessionViewerService.enableAllSessions();
      this.resizeState = {};
      this.sessionViewerService.resizeSessions();
    }
  }

  @HostListener('window:resize')
  onResize() {
    this.resetWidths();
  }

  onLeftArrowClick(session: TilingSession) {
    const leftIndexSession = this.getSessionByIndex(session.index - 1);

    if (leftIndexSession) {
      this.swapSessions(session, leftIndexSession);
    }
  }

  onRightArrowClick(session: TilingSession) {
    const rightIndexSession = this.getSessionByIndex(session.index + 1);

    if (rightIndexSession) {
      this.swapSessions(session, rightIndexSession);
    }
  }

  trackBySessionIndexAndId(_: number, session: TilingSession): string {
    return `${session.index}-${session.id}`;
  }

  isValidResizeState(state: ResizeState): state is ValidResizeState {
    return (
      state.index !== undefined &&
      state.startX !== undefined &&
      state.leftSession !== undefined &&
      state.rightSession !== undefined &&
      state.startWidthLeft !== undefined &&
      state.startWidthRight !== undefined
    );
  }

  private calculateNewWidths(
    validResizeState: ValidResizeState,
    delta: number,
  ): [number, number] {
    let newWidthLeft = validResizeState.startWidthLeft + delta;
    let newWidthRight = validResizeState.startWidthRight - delta;

    [newWidthLeft, newWidthRight] = this.adjustWidthsWithMinimum(
      validResizeState,
      newWidthLeft,
      newWidthRight,
    );
    return [newWidthLeft, newWidthRight];
  }

  private adjustWidthsWithMinimum(
    validResizeState: ValidResizeState,
    newWidthLeft: number,
    newWidthRight: number,
  ): [number, number] {
    if (newWidthLeft < this.minimumSessionWidth) {
      newWidthLeft = this.minimumSessionWidth;
      newWidthRight =
        validResizeState.startWidthLeft +
        validResizeState.startWidthRight -
        newWidthLeft;
    } else if (newWidthRight < this.minimumSessionWidth) {
      newWidthRight = this.minimumSessionWidth;
      newWidthLeft =
        validResizeState.startWidthLeft +
        validResizeState.startWidthRight -
        newWidthRight;
    }
    return [newWidthLeft, newWidthRight];
  }

  private resetWidths() {
    this.minimumSessionWidth = window.innerWidth * 0.15;
    this._tilingSessions.forEach(
      (session) =>
        (session.width = window.innerWidth / this._tilingSessions.length),
    );
    this.sessionViewerService.resizeSessions();
  }

  private getSessionByIndex(index: number): TilingSession | undefined {
    return this._tilingSessions.find((session) => session.index === index);
  }

  private swapSessions(
    firstSession: TilingSession,
    secondSession: TilingSession,
  ) {
    const firstSessionIndex = firstSession.index;
    const firstSessionWidth = firstSession.width;

    firstSession.index = secondSession.index;
    firstSession.width = secondSession.width;

    secondSession.index = firstSessionIndex;
    secondSession.width = firstSessionWidth;
  }
}

type ResizeState = {
  index?: number;
  startX?: number;
  leftSession?: TilingSession;
  rightSession?: TilingSession;
  startWidthLeft?: number;
  startWidthRight?: number;
};

type ValidResizeState = Required<ResizeState>;

type TilingSession = ViewerSession & {
  index: number;
  width: number;
  fullscreen: boolean;
};
