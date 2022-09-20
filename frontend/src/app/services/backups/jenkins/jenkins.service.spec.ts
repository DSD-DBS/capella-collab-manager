/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { JenkinsService } from './jenkins.service';

describe('JenkinsService', () => {
  let service: JenkinsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(JenkinsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
