/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class LocalStorageService {
  getValue(key: string): string {
    return localStorage.getItem(key) || '';
  }

  setValue(key: string, value: string) {
    localStorage.setItem(key, value);
  }
}
