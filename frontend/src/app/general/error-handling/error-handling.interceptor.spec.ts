import { TestBed } from '@angular/core/testing';

import { ErrorHandlingInterceptor } from './error-handling.interceptor';

describe('ErrorHandlingInterceptorService', () => {
  let service: ErrorHandlingInterceptor;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ErrorHandlingInterceptor);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
