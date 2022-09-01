/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { T4CSyncService } from './t4-csync.service';

describe('T4CSyncService', () => {
  let service: T4CSyncService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(T4CSyncService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
