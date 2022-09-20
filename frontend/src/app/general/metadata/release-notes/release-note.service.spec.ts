/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { ReleaseNoteService } from './release-note.service';

xdescribe('ReleaseNoteService', () => {
  let service: ReleaseNoteService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ReleaseNoteService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
