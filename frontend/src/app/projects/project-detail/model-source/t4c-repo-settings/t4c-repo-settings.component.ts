/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, Input, OnInit } from '@angular/core';

import { MatDialog } from '@angular/material/dialog';
import { T4CRepoService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Component({
  selector: 'app-t4c-repo-settings',
  templateUrl: './t4c-repo-settings.component.html',
  styleUrls: ['./t4c-repo-settings.component.css'],
})
export class T4CRepoSettingsComponent implements OnInit {
  constructor(public projectService: T4CRepoService) {}

  @Input()
  repository = '';

  ngOnInit(): void {}
}
