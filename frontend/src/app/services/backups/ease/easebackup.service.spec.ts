import { TestBed } from '@angular/core/testing';

import { EASEBackupService } from './easebackup.service';

describe('EASEBackupService', () => {
  let service: EASEBackupService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EASEBackupService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
