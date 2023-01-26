/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { ModelDiagramService } from './model-diagram.service';

describe('ModelDiagramService', () => {
  let service: ModelDiagramService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ModelDiagramService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
