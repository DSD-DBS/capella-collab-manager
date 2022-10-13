/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { GitModelService } from './git-model.service';

describe('GitModelService', () => {
  let service: GitModelService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GitModelService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
