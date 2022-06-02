// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { RepositoryService } from '../services/repository/repository.service';
import { Repository } from 'src/app/schemes';
import { SessionService } from '../services/session/session.service';

@Component({
  selector: 'app-workspace',
  templateUrl: './workspace.component.html',
  styleUrls: ['./workspace.component.css'],
})
export class WorkspaceComponent implements OnInit {
  repositories: Array<Repository> = [];
  showSpinner = true;

  constructor(
    public sessionService: SessionService,
    private repositoryService: RepositoryService
  ) {}

  ngOnInit() {
    this.showSpinner = true;
    this.repositoryService.getRepositories().subscribe(
      (res: Array<Repository>) => {
        this.repositories = res;
        this.showSpinner = false;
      },
      (err) => {
        this.showSpinner = false;
      }
    );
  }
}
