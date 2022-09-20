/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { T4cModelService } from '../../settings/t4c-model.service';

xdescribe('T4cModelService', () => {
  let service: T4cModelService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(T4cModelService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
