/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';

@Injectable({
  providedIn: 'root',
})
export class SessionHistoryService {
  LOCAL_STORAGE_SESSION_HISTORY_KEY = 'sessionRequestHistory';
  MAX_SESSIONS_IN_HISTORY = 3;

  constructor(private localStorageService: LocalStorageService) {}

  sessionHistory = new BehaviorSubject<SessionRequestHistory[] | undefined>(
    undefined,
  );

  getSessionRequestHistory(): SessionRequestHistory[] {
    let localStorageHistory: any; // eslint-disable-line @typescript-eslint/no-explicit-any
    try {
      localStorageHistory = JSON.parse(
        this.localStorageService.getValue(
          this.LOCAL_STORAGE_SESSION_HISTORY_KEY,
        ),
      );
    } catch (e) {
      console.error(e);
      return [];
    }

    if (!(localStorageHistory instanceof Array)) {
      return [];
    }

    const validSessionHistoryEntries: SessionRequestHistory[] = [];
    for (const entry of localStorageHistory) {
      if (this.isSessionRequestHistoryType(entry)) {
        entry.lastRequested = new Date(entry.lastRequested);
        validSessionHistoryEntries.push(entry);
      }
    }

    return validSessionHistoryEntries;
  }

  loadSessionRequestHistory() {
    this.sessionHistory.next(this.getSessionRequestHistory());
  }

  private isSessionRequestHistoryType(
    item: any, // eslint-disable-line @typescript-eslint/no-explicit-any
  ): item is SessionRequestHistory {
    return (
      typeof item === 'object' &&
      typeof item.toolId === 'number' &&
      typeof item.versionId === 'number' &&
      typeof item.connectionMethodId === 'string' &&
      typeof item.lastRequested === 'string'
    );
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
    this.localStorageService.setValue(
      this.LOCAL_STORAGE_SESSION_HISTORY_KEY,
      JSON.stringify(currentHistory),
    );
  }
}

export type SessionRequestHistory = {
  toolId: number;
  versionId: number;
  connectionMethodId: string;
  lastRequested: Date;
};
