import { TestBed } from '@angular/core/testing';

import { RepositoryProjectService } from './repository-project.service';

describe('RepositoryProjectService', () => {
  let service: RepositoryProjectService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RepositoryProjectService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
