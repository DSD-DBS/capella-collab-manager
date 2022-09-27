/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */


import { TestBed } from '@angular/core/testing';

import { IntegrationService } from './integration.service';

describe('IntegrationServiceService', () => {
  let service: IntegrationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(IntegrationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
