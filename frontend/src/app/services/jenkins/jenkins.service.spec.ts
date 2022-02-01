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
