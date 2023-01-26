/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { environment } from 'src/environments/environment';
import { BackendMetadata, VersionService } from './version.service';

@Component({
  selector: 'app-version',
  templateUrl: './version.component.html',
  styleUrls: ['./version.component.css'],
})
export class VersionComponent implements OnInit {
  backend: string = '-';
  frontend: string = '-';
  env: string = environment.environment || 'not specified';

  constructor(
    public versionService: VersionService,
    public dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.versionService
      .loadBackendMetadata()
      .subscribe((metadata: BackendMetadata) => {
        this.backend = `v${metadata.version}`;
      });
  }
}
