/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component } from '@angular/core';
import { OptionCardComponent } from './option-card/option-card.component';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  imports: [OptionCardComponent],
})
export class SettingsComponent {}
