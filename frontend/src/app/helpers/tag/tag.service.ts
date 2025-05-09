/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class TagHelperService {
  identifyColor(hexBgColor: string): string {
    const color = hexBgColor.substring(1, 7);
    const r = parseInt(color.substring(0, 2), 16);
    const g = parseInt(color.substring(2, 4), 16);
    const b = parseInt(color.substring(4, 6), 16);
    const shouldBeDark = r * 0.299 + g * 0.587 + b * 0.114 <= 186;
    return shouldBeDark ? 'white' : 'black';
  }
}
