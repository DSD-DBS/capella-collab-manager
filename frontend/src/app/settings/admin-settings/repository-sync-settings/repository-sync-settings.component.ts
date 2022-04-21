// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { RepositoryService } from 'src/app/services/repository/repository.service';
import { T4CSyncService } from 'src/app/services/t4c-sync/t4-csync.service';

@Component({
  selector: 'app-repository-sync-settings',
  templateUrl: './repository-sync-settings.component.html',
  styleUrls: ['./repository-sync-settings.component.css'],
})
export class RepositorySyncSettingsComponent implements OnInit {
  synchronizeButtonState = 'primary';

  constructor(
    private t4cSyncService: T4CSyncService,
    private repositoryService: RepositoryService
  ) {}

  ngOnInit(): void {}

  synchronizeRepositories() {
    this.t4cSyncService.syncRepositories().subscribe(() => {
      this.synchronizeButtonState = 'success';
      this.repositoryService.refreshRepositories();
      setTimeout(() => {
        this.synchronizeButtonState = 'primary';
      }, 3000);
    });
  }
}
