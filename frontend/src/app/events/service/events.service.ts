/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Project } from 'src/app/projects/service/project.service';
import { User } from 'src/app/services/user/user.service';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class EventsService {
  BACKEND_URL_PREFIX = environment.backend_url + '/users/';

  private _historyEvents = new BehaviorSubject<HistoryEvent[]>([]);
  readonly historyEvents = this._historyEvents.asObservable();

  constructor(private http: HttpClient) {}

  loadHistoryEvents(): void {
    this.http
      .get<HistoryEvent[]>(this.BACKEND_URL_PREFIX + 'history/events')
      .subscribe((events) => this._historyEvents.next(events));
  }

  customSortingDataAccessor(
    data: HistoryEvent,
    sortHeaderId: string,
  ): string | number {
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
        return data.reason;
      default:
        return '';
    }
  }
}

export type HistoryEvent = {
  id: number;
  execution_time: string;
  event_type: EventType;
  user: User;
  executor?: User;
  project?: Project;
  reason: string;
};

export type EventType =
  | 'CreatedUser'
  | 'AddedToProject'
  | 'RemovedFromProject'
  | 'AssignedProjectRoleUser'
  | 'AssignedProjectRoleManager'
  | 'AssignedProjectPermission'
  | 'AssignedProjectPermissionReadWrite'
  | 'AssignedRoleAdmin'
  | 'AssignedRoleUser';
