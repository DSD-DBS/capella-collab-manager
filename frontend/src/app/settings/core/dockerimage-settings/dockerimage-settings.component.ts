/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';

@Component({
  selector: 'app-dockerimage-settings',
  templateUrl: './dockerimage-settings.component.html',
  styleUrls: ['./dockerimage-settings.component.css'],
})
export class DockerimageSettingsComponent implements OnInit {
  constructor(private navbarService: NavBarService) {
    this.navbarService.title = 'Settings / Core / Dockerimages';
  }

  ngOnInit(): void {}
}
