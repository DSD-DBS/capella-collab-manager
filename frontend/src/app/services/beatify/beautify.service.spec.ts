/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { BeautifyService } from './beautify.service';

describe('BeautifyService', () => {
  let service: BeautifyService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BeautifyService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
