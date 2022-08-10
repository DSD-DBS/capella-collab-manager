// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { TestBed } from '@angular/core/testing';

import { LoadFilesService } from './load-files.service';

describe('LoadFilesService', () => {
  let service: LoadFilesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LoadFilesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
