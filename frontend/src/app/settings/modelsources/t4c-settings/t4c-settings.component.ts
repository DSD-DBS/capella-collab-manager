// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import { T4CSyncService } from 'src/app/services/t4c-sync/t4-csync.service';

@Component({
  selector: 'app-t4c-settings',
  templateUrl: './t4c-settings.component.html',
  styleUrls: ['./t4c-settings.component.css'],
})
export class T4CSettingsComponent implements OnInit {
  constructor(private navbarService: NavBarService) {
    this.navbarService.title = 'Settings / Modelsources / T4C';
  }

  ngOnInit(): void {}
}
