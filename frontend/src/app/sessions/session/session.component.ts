/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, HostListener, OnInit } from '@angular/core';
import { MatLegacyCheckboxChange as MatCheckboxChange } from '@angular/material/legacy-checkbox';
import { DomSanitizer } from '@angular/platform-browser';
import { filter, take } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { Session } from 'src/app/schemes';
import { GuacamoleService } from 'src/app/services/guacamole/guacamole.service';
import { SessionService } from 'src/app/sessions/service/session.service';
import { UserSessionService } from 'src/app/sessions/service/user-session.service';

@Component({
  selector: 'app-session',
  templateUrl: './session.component.html',
  styleUrls: ['./session.component.css'],
})
export class SessionComponent implements OnInit {
  cachedSessions?: CachedSession[] = undefined;
  selectedSessions: Session[] = [];
  private debounceTimer?: number;

  draggingActive = false;

  constructor(
    public userSessionService: UserSessionService,
    public sessionService: SessionService,
    private guacamoleService: GuacamoleService,
    private localStorageService: LocalStorageService,
    private domSanitizer: DomSanitizer
  ) {
    this.userSessionService.loadSessions();
  }

  get checkedSessions(): undefined | CachedSession[] {
    return this.cachedSessions?.filter((session) => session.checked);
  }

  changeSessionSelection(event: MatCheckboxChange, session: CachedSession) {
    session.checked = event.checked;
  }

  ngOnInit(): void {
    this.initializeCachedSessions();
    this.handleEventsToDetermineFocus();
  }

  initializeCachedSessions() {
    this.userSessionService.sessions$
      .pipe(
        filter((sessions) => sessions !== undefined),
        take(1)
      )
      .subscribe((sessions) => {
        this.cachedSessions = sessions?.map((session) => {
          (session as CachedSession).checked = false;
          return session;
        });
      });
  }

  handleEventsToDetermineFocus() {
    window.focus();
    window.addEventListener('blur', () => {
      const focusedSession = this.selectedSessions.find(
        (session) => 'session-' + session.id === document.activeElement?.id
      );
      if (!focusedSession) {
        return;
      }

      document.getElementById('session-' + focusedSession.id)?.focus();
      focusedSession.focused = true;

      this.selectedSessions
        .filter((session) => session !== focusedSession)
        .map((session) => {
          session.focused = false;
        });
    });
  }

  selectSessions() {
    this.checkedSessions?.forEach((session) => {
      session.focused = false;
      if (session.jupyter_uri) {
        session.safeResourceURL =
          this.domSanitizer.bypassSecurityTrustResourceUrl(session.jupyter_uri);
        session.reloadToResize = false;
        this.selectedSessions.push(session);
      } else {
        this.guacamoleService.getGucamoleToken(session?.id).subscribe((res) => {
          this.localStorageService.setValue('GUAC_AUTH', res.token);
          session.safeResourceURL =
            this.domSanitizer.bypassSecurityTrustResourceUrl(res.url);
          session.reloadToResize = true;
          this.selectedSessions.push(session);
        });
      }
    });
  }

  focusSession(session: Session) {
    document.getElementById('session-' + session.id)?.focus();
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
      Array.from(document.getElementsByTagName('iframe')).forEach((iframe) => {
        const session = this.selectedSessions.find(
          (session) => 'session-' + session.id === iframe.id
        );

        if (session?.reloadToResize) {
          this.reloadIFrame(iframe);
        }
      });
    }, 250);
  }

  reloadIFrame(iframe: HTMLIFrameElement) {
    const src = iframe.src;

    iframe.removeAttribute('src');

    setTimeout(() => {
      iframe.src = src;
    }, 100);
  }
}

type CachedSession = Session & {
  checked?: boolean;
};
