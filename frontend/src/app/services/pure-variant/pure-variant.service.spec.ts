/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { PureVariantService } from './pure-variant.service';

xdescribe('PureVariantService', () => {
  let service: PureVariantService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PureVariantService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
