/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { TestBed } from '@angular/core/testing';

import { GitSettingsService } from './git-settings.service';

xdescribe('GitSettingsService', () => {
  let service: GitSettingsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GitSettingsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
