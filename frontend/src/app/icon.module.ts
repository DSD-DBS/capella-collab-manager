/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgModule, inject } from '@angular/core';
import { MatIconRegistry } from '@angular/material/icon';

@NgModule({})
export class IconModule {
  private matIconReg = inject(MatIconRegistry);

  constructor() {
    this.matIconReg.setDefaultFontSetClass('material-symbols-outlined');
  }
}
