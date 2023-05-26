/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { PluginStoreService } from 'src/app/plugins/store/service/plugin-store.service';

@Component({
  selector: 'app-plugin-store-overview',
  templateUrl: './plugin-store-overview.component.html',
  styleUrls: ['./plugin-store-overview.component.css'],
})
export class PluginStoreOverviewComponent {
  constructor(public pluginStoreService: PluginStoreService) {}
}
