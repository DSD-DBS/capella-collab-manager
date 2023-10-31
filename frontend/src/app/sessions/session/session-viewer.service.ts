/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { BehaviorSubject, map } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { Session } from 'src/app/schemes';
import { GuacamoleService } from 'src/app/services/guacamole/guacamole.service';

@Injectable({
  providedIn: 'root',
})
export class SessionViewerService {
  constructor(
    private guacamoleService: GuacamoleService,
    private localStorageService: LocalStorageService,
    private domSanitizer: DomSanitizer,
  ) {}

  private _sessions = new BehaviorSubject<ViewerSession[] | undefined>(
    undefined,
  );

  public readonly sessions$ = this._sessions.pipe(
    map((sessions) => {
      const fullscreenSession = sessions?.find((session) => session.fullscreen);
      return fullscreenSession ? [fullscreenSession] : sessions;
    }),
  );

  pushJupyterSession(session: Session): void {
    if (session.jupyter_uri) {
      const viewerSession = session as ViewerSession;

      viewerSession.focused = false;
      viewerSession.safeResourceURL =
        this.domSanitizer.bypassSecurityTrustResourceUrl(session.jupyter_uri);
      viewerSession.reloadToResize = false;

      this.insertViewerSession(viewerSession);
    }
  }

  pushGuacamoleSession(session: Session): void {
    const viewerSession = session as ViewerSession;

    this.guacamoleService.getGucamoleToken(session.id).subscribe({
      next: (guacamoleAuthInfo) => {
        this.localStorageService.setValue('GUAC_AUTH', guacamoleAuthInfo.token);

        viewerSession.focused = false;
        viewerSession.safeResourceURL =
          this.domSanitizer.bypassSecurityTrustResourceUrl(
            guacamoleAuthInfo.url,
          );
        viewerSession.reloadToResize = true;

        this.insertViewerSession(viewerSession);
      },
    });
  }

  focusSession(session: Session): void {
    document.getElementById('session-' + session.id)?.focus();

    const updatedSessions = this._sessions.value?.map((curSession) => ({
      ...curSession,
      focused: session.id === curSession.id,
    }));

    this._sessions.next(updatedSessions);
  }

  resizeSessions(): void {
    document.querySelectorAll('iframe').forEach((iframe) => {
      const session = this._sessions.value?.find(
        (session) => `session-${session.id}` === iframe.id,
      );

      if (session?.reloadToResize) {
        this.reloadIFrame(iframe);
      }
    });
  }

  resizeSession(session: ViewerSession): void {
    const sessionIFrame = document.querySelector<HTMLIFrameElement>(
      `iframe#session-${session.id}`,
    );

    if (sessionIFrame && session.reloadToResize) {
      this.reloadIFrame(sessionIFrame);
    }
  }

  toggleFullscreen(session: ViewerSession): void {
    const updatedSessions = this._sessions.value?.map((curSession) => {
      if (session.id === curSession.id) {
        return { ...curSession, fullscreen: !curSession.fullscreen };
      }
      return curSession;
    });
    this._sessions.next(updatedSessions);
    this.resizeSession(session);
  }

  clearSessions(): void {
    this._sessions.next(undefined);
  }

  private reloadIFrame(iframe: HTMLIFrameElement) {
    const src = iframe.src;

    iframe.removeAttribute('src');

    setTimeout(() => {
      iframe.src = src;
    }, 100);
  }

  private insertViewerSession(viewerSession: ViewerSession): void {
    const currentSessions = this._sessions.value;

    if (currentSessions === undefined) {
      this._sessions.next([viewerSession]);
    } else {
      this._sessions.next([...currentSessions, viewerSession]);
    }
  }
}

export type ViewerSession = Session & {
  safeResourceURL?: SafeResourceUrl;
  focused: boolean;
  reloadToResize: boolean;
  fullscreen: boolean;
};
