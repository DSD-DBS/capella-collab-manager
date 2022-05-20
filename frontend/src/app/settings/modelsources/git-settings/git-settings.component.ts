// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';

@Component({
  selector: 'app-git-settings',
  templateUrl: './git-settings.component.html',
  styleUrls: ['./git-settings.component.css'],
})
export class GitSettingsComponent implements OnInit {
  constructor(private navbarService: NavBarService) {
    this.navbarService.title = 'Settings / Modelsources / Git';
  }

  ngOnInit(): void {}
}
