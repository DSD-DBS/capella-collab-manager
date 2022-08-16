import { TestBed } from '@angular/core/testing';

import { SourceService } from './source.service';

describe('SourceService', () => {
  let service: SourceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SourceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
