/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Subscription, filter, take } from 'rxjs';
import { SessionService } from 'src/app/sessions/service/session.service';
import { SessionHistoryService } from 'src/app/sessions/user-sessions-wrapper/create-sessions/create-session-history/session-history.service';
import {
  ConnectionMethod,
  Tool,
  ToolService,
  ToolVersion,
} from 'src/app/settings/core/tools-settings/tool.service';

@Component({
  selector: 'app-create-session-history',
  standalone: true,
  imports: [CommonModule, MatIconModule, MatProgressSpinnerModule],
  templateUrl: './create-session-history.component.html',
  styles: ``,
})
export class CreateSessionHistoryComponent implements OnInit {
  resolvedHistory: ResolvedSessionRequestHistory[] = [];
  sessionsToBeLoaded = 3;
  sessionsLoaded = 0;

  activeSubscriptions: Subscription[] = [];

  get sortedResolvedHistory() {
    return this.resolvedHistory.sort(
      (a, b) => b.lastTimeRequested.getTime() - a.lastTimeRequested.getTime(),
    );
  }

  constructor(
    private toolService: ToolService,
    private sessionHistoryService: SessionHistoryService,
    private sessionService: SessionService,
  ) {}

  ngOnInit() {
    this.loadLastSessions();
    this.sessionHistoryService.loadSessionRequestHistory();
  }

  loadLastSessions() {
    this.toolService._tools
      .pipe(filter(Boolean), take(1))
      .subscribe((tools) => {
        this.sessionHistoryService.sessionHistory
          .pipe(filter(Boolean))
          .subscribe((sessions) => {
            this.resolvedHistory = [];
            this.sessionsToBeLoaded = sessions.length;
            this.sessionsLoaded = 0;

            for (const subscription of this.activeSubscriptions) {
              subscription.unsubscribe();
            }

            for (const session of sessions) {
              this.activeSubscriptions.push(
                this.toolService
                  .getVersionsForTool(session.toolId, true)
                  .subscribe({
                    next: (versions) => {
                      const tool = tools.find((t) => t.id === session.toolId);
                      const version = versions.find(
                        (v) => v.id === session.versionId,
                      );
                      const connectionMethod =
                        tool?.config.connection.methods.find(
                          (cm) => cm.id === session.connectionMethodId,
                        );
                      this.sessionsLoaded++;
                      if (
                        tool !== undefined &&
                        version !== undefined &&
                        connectionMethod !== undefined
                      ) {
                        this.resolvedHistory.push({
                          tool: tool,
                          version: version,
                          connectionMethod: connectionMethod,
                          lastTimeRequested: session.lastRequested,
                          loading: false,
                        });
                      }
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
      .createSession(
        session.tool.id,
        session.version.id,
        session.connectionMethod.id,
        'persistent',
        [],
      )
      .subscribe({
        next: () => {
          session.loading = false;
        },
        error: () => {
          session.loading = false;
        },
      });
  }
}

export type ResolvedSessionRequestHistory = {
  tool: Tool;
  version: ToolVersion;
  connectionMethod: ConnectionMethod;
  loading: boolean;
  lastTimeRequested: Date;
};
