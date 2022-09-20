/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { VersionService } from '../version/version.service';

@Component({
  selector: 'app-release-notes',
  templateUrl: './release-notes.component.html',
  styleUrls: ['./release-notes.component.css'],
})
export class ReleaseNotesComponent implements OnInit {
  constructor(public versionService: VersionService) {}

  ngOnInit(): void {}
}
