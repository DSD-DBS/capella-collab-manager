import { TestBed } from '@angular/core/testing';

import { HttpResponseInterceptor } from './http-response.interceptor';

describe('HttpResponseInterceptor', () => {
  beforeEach(() => TestBed.configureTestingModule({
    providers: [
      HttpResponseInterceptor
      ]
  }));

  it('should be created', () => {
    const interceptor: HttpResponseInterceptor = TestBed.inject(HttpResponseInterceptor);
    expect(interceptor).toBeTruthy();
  });
});
