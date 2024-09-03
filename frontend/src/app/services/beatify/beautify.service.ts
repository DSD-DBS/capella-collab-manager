/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class BeautifyService {
  beatifyDate(date: string): string {
    const newDate = new Date(date);
    const now = new Date();
    let newDateString = '';
    if (
      newDate.getFullYear() == now.getFullYear() &&
      newDate.getMonth() == now.getMonth() &&
      newDate.getDate() == now.getDate()
    ) {
      newDateString = 'today';
    } else {
      newDateString =
        'on ' +
        newDate.toLocaleDateString(undefined, {
          year: 'numeric',
          month: 'numeric',
          day: 'numeric',
        });
    }

    return (
      newDateString +
      ' at ' +
      newDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    );
  }
}
