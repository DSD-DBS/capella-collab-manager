/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { ReleaseNote, ReleaseNoteService } from './release-note.service';

@Component({
  selector: 'app-release-notes',
  templateUrl: './release-notes.component.html',
  styleUrls: ['./release-notes.component.css'],
})
export class ReleaseNotesComponent implements OnInit {
  version = '0.0.5';

  releaseNotes: Array<ReleaseNote> = [];

  constructor(private releaseNoteService: ReleaseNoteService) {
    this.releaseNoteService
      .loadReleaseNotes()
      .subscribe((releaseNotes: Array<ReleaseNote>) => {
        this.releaseNotes = releaseNotes;
      });
  }

  ngOnInit(): void {}
}
