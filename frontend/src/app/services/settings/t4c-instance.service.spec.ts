/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { T4CInstanceService } from './t4c-instance.service';

xdescribe('T4CInstanceService', () => {
  let service: T4CInstanceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(T4CInstanceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
