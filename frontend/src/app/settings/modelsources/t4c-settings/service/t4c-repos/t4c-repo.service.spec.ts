// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { TestBed } from '@angular/core/testing';

import { T4CRepoService } from './t4c-repo.service';

describe('T4CRepoService', () => {
  let service: T4CRepoService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(T4CRepoService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
