/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { RepositoryUserService } from './repository-user.service';

xdescribe('RepositoryUserService', () => {
  let service: RepositoryUserService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RepositoryUserService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
