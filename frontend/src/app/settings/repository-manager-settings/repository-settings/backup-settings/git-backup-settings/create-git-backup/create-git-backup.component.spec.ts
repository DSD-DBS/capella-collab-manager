import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateGitBackupComponent } from './create-git-backup.component';

describe('CreateGitBackupComponent', () => {
  let component: CreateGitBackupComponent;
  let fixture: ComponentFixture<CreateGitBackupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CreateGitBackupComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateGitBackupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
