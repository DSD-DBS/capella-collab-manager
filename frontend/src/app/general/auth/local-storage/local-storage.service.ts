/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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

  setValue(key: string, value: any) {
    localStorage.setItem(key, value);
  }
}
