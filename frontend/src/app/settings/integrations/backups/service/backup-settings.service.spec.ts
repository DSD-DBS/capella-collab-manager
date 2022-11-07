/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { BackupSettingsService } from './backup-settings.service';

describe('BackupSettingsService', () => {
  let service: BackupSettingsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BackupSettingsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
