import { TestBed } from '@angular/core/testing';

import { BeautifyService } from './beautify.service';

describe('BeautifyService', () => {
  let service: BeautifyService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BeautifyService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
