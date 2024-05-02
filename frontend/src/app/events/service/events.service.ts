/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { HistoryEvent } from 'src/app/openapi';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class EventsService {
  private _historyEvents = new BehaviorSubject<HistoryEvent[]>([]);
  readonly historyEvents = this._historyEvents.asObservable();

  constructor(private http: HttpClient) {}

  loadHistoryEvents(): void {
    this.http
      .get<HistoryEvent[]>(`${environment.backend_url}/events`)
      .subscribe((events) => this._historyEvents.next(events));
  }

  customSortingDataAccessor(data: HistoryEvent, sortHeaderId: string): string {
    switch (sortHeaderId) {
      case 'eventType':
        return data.event_type;
      case 'userName':
        return data.user.name;
      case 'executorName':
        return data.executor ? data.executor.name : 'System';
      case 'executionTime':
        return data.execution_time;
      case 'projectName':
        return data.project ? data.project.name : '';
      case 'reason':
        return data.reason || '';
      default:
        return '';
    }
  }
}
