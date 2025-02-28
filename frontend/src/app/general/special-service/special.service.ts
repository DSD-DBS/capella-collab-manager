/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { computed, Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class SpecialService {
  enabled = computed(() => {
    const today = new Date();
    return today.getMonth() === 3 && today.getDate() === 1;
  });
}
