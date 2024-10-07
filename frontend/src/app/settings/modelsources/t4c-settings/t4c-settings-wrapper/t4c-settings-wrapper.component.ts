/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnDestroy, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import { T4CLicenseServerWrapperService } from '../../../../services/settings/t4c-license-server.service';

@Component({
  selector: 'app-t4c-settings-wrapper',
  templateUrl: './t4c-settings-wrapper.component.html',
  styleUrls: ['./t4c-settings-wrapper.component.css'],
  standalone: true,
  imports: [RouterOutlet],
})
export class T4CSettingsWrapperComponent implements OnInit, OnDestroy {
  constructor(
    public t4cInstanceService: T4CInstanceWrapperService,
    public t4cLicenseServerService: T4CLicenseServerWrapperService,
  ) {}

  ngOnInit(): void {
    this.t4cInstanceService.loadInstances();
    this.t4cLicenseServerService.loadLicenseServers();
  }

  ngOnDestroy(): void {
    this.t4cInstanceService.reset();
  }
}
