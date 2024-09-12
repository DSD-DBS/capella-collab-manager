/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgModule } from '@angular/core';
import { MatIconRegistry } from '@angular/material/icon';

@NgModule({})
export class IconModule {
  constructor(private matIconReg: MatIconRegistry) {
    this.matIconReg.setDefaultFontSetClass('material-symbols-outlined');
  }
}
