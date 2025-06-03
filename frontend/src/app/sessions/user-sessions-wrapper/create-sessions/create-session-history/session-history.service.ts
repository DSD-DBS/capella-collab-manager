/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import * as v from 'valibot';

const sessionRequestHistorySchema = v.object({
  toolId: v.number(),
  versionId: v.number(),
  connectionMethodId: v.string(),
  lastRequested: v.pipe(
    v.string(),
    v.transform((dateString) => new Date(dateString)),
  ),
});

const sessionHistoryArraySchema = v.array(sessionRequestHistorySchema);
export type SessionRequestHistory = v.InferOutput<
  typeof sessionRequestHistorySchema
>;

@Injectable({
  providedIn: 'root',
})
export class SessionHistoryService {
  LOCAL_STORAGE_SESSION_HISTORY_KEY = 'sessionRequestHistory';
  MAX_SESSIONS_IN_HISTORY = 3;

  sessionHistory = new BehaviorSubject<SessionRequestHistory[] | undefined>(
    undefined,
  );

  getSessionRequestHistory(): SessionRequestHistory[] {
    const currentSessionHistory = localStorage.getItem(
      this.LOCAL_STORAGE_SESSION_HISTORY_KEY,
    );
    if (!currentSessionHistory) {
      return [];
    }

    try {
      return v.parse(
        sessionHistoryArraySchema,
        JSON.parse(currentSessionHistory),
      );
    } catch (e) {
      console.error(e);
      localStorage.removeItem(this.LOCAL_STORAGE_SESSION_HISTORY_KEY);
      return [];
    }
  }

  loadSessionRequestHistory() {
    this.sessionHistory.next(this.getSessionRequestHistory());
  }

  addSessionRequestToHistory(history: SessionRequestHistory) {
    let currentHistory = this.getSessionRequestHistory();
    currentHistory = currentHistory
      .filter(
        (entry) =>
          entry.toolId !== history.toolId ||
          entry.versionId !== history.versionId ||
          entry.connectionMethodId !== history.connectionMethodId,
      )
      .sort((a, b) => a.lastRequested.getTime() - b.lastRequested.getTime());

    currentHistory.push(history);

    if (currentHistory.length > this.MAX_SESSIONS_IN_HISTORY) {
      currentHistory.shift();
    }

    this.sessionHistory.next(currentHistory);
    localStorage.setItem(
      this.LOCAL_STORAGE_SESSION_HISTORY_KEY,
      JSON.stringify(currentHistory),
    );
  }
}
