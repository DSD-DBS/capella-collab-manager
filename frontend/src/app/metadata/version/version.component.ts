/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { environment } from 'src/environments/environment';
import { ReleaseNotesComponent } from '../release-notes/release-notes.component';
import { BackendMetadata, Version, VersionService } from './version.service';

@Component({
  selector: 'app-version',
  templateUrl: './version.component.html',
  styleUrls: ['./version.component.css'],
})
export class VersionComponent implements OnInit {
  backend: string = '-';
  frontend: string = '-';
  env: string =
    ((environment as any)['production'] && 'production') || 'development';

  constructor(
    public versionService: VersionService,
    public dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.versionService
      .loadBackendMetadata()
      .subscribe((metadata: BackendMetadata) => {
        this.backend = metadata.version;
      });
  }

  openReleaseNotes(): void {
    this.dialog.open(ReleaseNotesComponent);
  }
}
