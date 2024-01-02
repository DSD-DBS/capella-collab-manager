/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class NoticeService {
  notices: Notice[] = [];
  noticeLevels = [
    'primary',
    'secondary',
    'success',
    'danger',
    'warning',
    'info',
    'alert',
  ];

  constructor(private http: HttpClient) {
    this.refreshNotices();
  }

  refreshNotices(): void {
    this.getNotices().subscribe((res) => {
      this.notices = res;
    });
  }

  getNotices(): Observable<Notice[]> {
    return this.http.get<Notice[]>(environment.backend_url + '/notices');
  }

  deleteNotice(id: number): Observable<void> {
    return this.http.delete<void>(environment.backend_url + '/notices/' + id);
  }

  createNotice(body: CreateNotice): Observable<Notice> {
    return this.http.post<Notice>(environment.backend_url + '/notices', body);
  }
}

export interface Notice extends CreateNotice {
  id: number;
}

export interface CreateNotice {
  level: NoticeLevel;
  title: string;
  message: string;
}

export type NoticeLevel =
  | 'primary'
  | 'secondary'
  | 'success'
  | 'danger'
  | 'warning'
  | 'info'
  | 'alert';
