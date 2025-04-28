/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component } from '@angular/core';
import { MatRipple } from '@angular/material/core';
import { RouterLink } from '@angular/router';
import { MatIconComponent } from '../helpers/mat-icon/mat-icon.component';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  imports: [RouterLink, MatRipple, MatIconComponent],
  styleUrls: ['./settings.component.css'],
})
export class SettingsComponent {}
