/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class FullscreenService {
  private _isFullscreen = new BehaviorSubject<boolean>(false);
  isFullscreen$ = this._isFullscreen.asObservable();

  toggleFullscreen(): void {
    this._isFullscreen.next(!this._isFullscreen.value);
  }

  disableFullscreen(): void {
    this._isFullscreen.next(false);
  }
}
