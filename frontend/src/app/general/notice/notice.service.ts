/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { NoticeResponse, NoticesService } from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class NoticeWrapperService {
  private _notices = new BehaviorSubject<NoticeResponse[] | undefined>(
    undefined,
  );
  public readonly notices$ = this._notices.asObservable();

  constructor(private noticesService: NoticesService) {
    this.refreshNotices();
  }

  refreshNotices(): void {
    this._notices.next(undefined);
    this.noticesService.getNotices().subscribe((res) => {
      this._notices.next(res);
    });
  }
}
