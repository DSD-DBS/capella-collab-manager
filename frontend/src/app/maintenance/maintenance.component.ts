// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { NavBarService } from '../navbar/service/nav-bar.service';

@Component({
  selector: 'app-maintenance',
  templateUrl: './maintenance.component.html',
  styleUrls: ['./maintenance.component.css'],
})
export class MaintenanceComponent implements OnInit {
  constructor(private navbarService: NavBarService) {
    this.navbarService.disableAll();
  }

  ngOnInit(): void {}
}
