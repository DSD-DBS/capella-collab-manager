// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { TestBed } from '@angular/core/testing';

import { OwnSessionService } from './own-session.service';

describe('OwnSessionService', () => {
  let service: OwnSessionService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(OwnSessionService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
