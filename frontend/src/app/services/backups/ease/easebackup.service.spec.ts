/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { EASEBackupService } from './easebackup.service';

xdescribe('EASEBackupService', () => {
  let service: EASEBackupService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EASEBackupService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
