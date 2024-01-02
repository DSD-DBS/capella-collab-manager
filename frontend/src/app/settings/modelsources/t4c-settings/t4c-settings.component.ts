/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { T4CInstanceService } from 'src/app/services/settings/t4c-instance.service';

@Component({
  selector: 'app-t4c-settings',
  templateUrl: './t4c-settings.component.html',
  styleUrls: ['./t4c-settings.component.css'],
})
export class T4CSettingsComponent {
  constructor(public t4cInstanceService: T4CInstanceService) {}
}
