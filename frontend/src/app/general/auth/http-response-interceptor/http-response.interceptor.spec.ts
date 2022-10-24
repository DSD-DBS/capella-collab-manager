/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { TestBed } from '@angular/core/testing';

import { HttpResponseInterceptor } from './http-response.interceptor';

xdescribe('HttpResponseInterceptor', () => {
  beforeEach(() =>
    TestBed.configureTestingModule({
      providers: [HttpResponseInterceptor],
    })
  );

  it('should be created', () => {
    const interceptor: HttpResponseInterceptor = TestBed.inject(
      HttpResponseInterceptor
    );
    expect(interceptor).toBeTruthy();
  });
});
