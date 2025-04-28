/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subscription, filter, take } from 'rxjs';
import { SessionType, Tool, ToolVersion } from 'src/app/openapi';
import { SessionService } from 'src/app/sessions/service/session.service';
import {
  SessionHistoryService,
  SessionRequestHistory,
} from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-session-history/session-history.service';
import {
  ConnectionMethod,
  ToolWrapperService,
} from 'src/app/settings/core/tools-settings/tool.service';
import { RelativeTimeComponent } from '../../../../general/relative-time/relative-time.component';

@Component({
  selector: 'app-create-session-history',
  imports: [
    CommonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    RelativeTimeComponent,
  ],
  templateUrl: './create-session-history.component.html',
  styles: ``,
})
export class CreateSessionHistoryComponent implements OnInit, OnDestroy {
  private toolService = inject(ToolWrapperService);
  private sessionHistoryService = inject(SessionHistoryService);
  private sessionService = inject(SessionService);

  resolvedHistory: ResolvedSessionRequestHistory[] = [];
  sessionsToBeLoaded = this.sessionHistoryService.MAX_SESSIONS_IN_HISTORY;
  sessionsLoaded = 0;

  activeSubscriptions: Subscription[] = [];

  get sortedResolvedHistory() {
    return this.resolvedHistory.sort(
      (a, b) => b.lastTimeRequested.getTime() - a.lastTimeRequested.getTime(),
    );
  }

  ngOnInit() {
    this.sessionHistoryService.loadSessionRequestHistory();
    this.loadLastSessions();
  }

  pushValidResolvedSessionToHistory(
    tool: Tool,
    version: ToolVersion,
    session: SessionRequestHistory,
  ) {
    const connectionMethod = this.toolService.getConnectionIdForTool(
      tool,
      session.connectionMethodId,
    );
    if (connectionMethod === undefined) return;

    this.resolvedHistory.push({
      tool: tool,
      version: version,
      connectionMethod: connectionMethod,
      lastTimeRequested: session.lastRequested,
      loading: false,
    });
  }

  loadLastSessions() {
    this.toolService._tools.pipe(filter(Boolean), take(1)).subscribe(() => {
      this.sessionHistoryService.sessionHistory
        .pipe(filter(Boolean), take(1))
        .subscribe((sessions) => {
          this.resolvedHistory = [];
          this.sessionsToBeLoaded = sessions.length;
          this.sessionsLoaded = 0;

          this.unsubscribeAll();

          for (const session of sessions) {
            this.activeSubscriptions.push(
              this.toolService
                .getVersionForTool(session.toolId, session.versionId, true)
                .subscribe({
                  next: (version) => {
                    this.sessionsLoaded++;

                    const tool = this.toolService.getCachedToolById(
                      session.toolId,
                    );
                    if (tool === undefined) return;

                    this.pushValidResolvedSessionToHistory(
                      tool,
                      version,
                      session,
                    );
                  },
                  error: () => {
                    this.sessionsLoaded++;
                  },
                }),
            );
          }
        });
    });
  }

  requestSession(session: ResolvedSessionRequestHistory) {
    session.loading = true;
    this.sessionService
      .createSession({
        tool_id: session.tool.id,
        version_id: session.version.id,
        connection_method_id: session.connectionMethod.id!,
        session_type: SessionType.Persistent,
      })
      .subscribe({
        next: () => {
          session.loading = false;
        },
        error: () => {
          session.loading = false;
        },
      });
  }

  unsubscribeAll() {
    for (const subscription of this.activeSubscriptions) {
      subscription.unsubscribe();
    }
  }

  ngOnDestroy() {
    this.unsubscribeAll();
  }
}

export interface ResolvedSessionRequestHistory {
  tool: Tool;
  version: ToolVersion;
  connectionMethod: ConnectionMethod;
  loading: boolean;
  lastTimeRequested: Date;
}
