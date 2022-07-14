import { TestBed } from '@angular/core/testing';

import { LoadFilesService } from './load-files.service';

describe('LoadFilesService', () => {
  let service: LoadFilesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LoadFilesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
