/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import { NoticeWrapperService } from 'src/app/general/notice/notice.service';
import { NoticeLevel, NoticeResponse } from 'src/app/openapi';

export const mockNotice: NoticeResponse = {
  id: 1,
  title: 'Title of the notice',
  message:
    'This is the message / content of a notice. It can also contain simple HTML like links: ' +
    "<a href='https://example.com'>example.com</a>",
  level: NoticeLevel.Info,
};

class MockNoticeWrapperService implements Partial<NoticeWrapperService> {
  private _notices = new BehaviorSubject<NoticeResponse[] | undefined>(
    undefined,
  );
  public readonly notices$ = this._notices.asObservable();

  constructor(notices: NoticeResponse[]) {
    this._notices.next(notices);
  }
}

export const mockNoticeWrapperServiceProvider = (notices: NoticeResponse[]) => {
  return {
    provide: NoticeWrapperService,
    useValue: new MockNoticeWrapperService(notices),
  };
};
