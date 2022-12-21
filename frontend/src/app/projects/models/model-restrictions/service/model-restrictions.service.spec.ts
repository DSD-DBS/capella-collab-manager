/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { ModelRestrictionsService } from './model-restrictions.service';

describe('ModelRestrictionsService', () => {
  let service: ModelRestrictionsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ModelRestrictionsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
