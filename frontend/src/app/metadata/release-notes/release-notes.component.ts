/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { Version, VersionService } from '../version/version.service';
import { ReleaseNote } from './release-note.service';

@Component({
  selector: 'app-release-notes',
  templateUrl: './release-notes.component.html',
  styleUrls: ['./release-notes.component.css'],
})
export class ReleaseNotesComponent implements OnInit {
  version = '0.0.5';

  releaseNotes: Array<ReleaseNote> = [];

  constructor(private versionService: VersionService) {
    this.versionService.loadVersion().subscribe((version: Version) => {
      this.releaseNotes = version.github;
    });
  }

  ngOnInit(): void {}
}
