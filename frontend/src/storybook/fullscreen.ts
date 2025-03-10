/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { BehaviorSubject } from 'rxjs';
import { FullscreenService } from 'src/app/sessions/service/fullscreen.service';

class MockFullscreenService implements Partial<FullscreenService> {
  private _isFullscreen = new BehaviorSubject<boolean>(false);
  isFullscreen$ = this._isFullscreen.asObservable();

  constructor(isFullscreen: boolean) {
    this._isFullscreen.next(isFullscreen);
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  toggleFullscreen(): void {}

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  disableFullscreen(): void {}
}

export const mockFullscreenServiceProvider = (isFullscreen: boolean) => {
  return {
    provide: FullscreenService,
    useValue: new MockFullscreenService(isFullscreen),
  };
};
