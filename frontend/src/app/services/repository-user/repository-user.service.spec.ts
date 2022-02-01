import { TestBed } from '@angular/core/testing';

import { RepositoryUserService } from './repository-user.service';

describe('RepositoryUserService', () => {
  let service: RepositoryUserService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RepositoryUserService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
