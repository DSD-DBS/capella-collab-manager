import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GitBackupSettingsComponent } from './git-backup-settings.component';

describe('GitBackupSettingsComponent', () => {
  let component: GitBackupSettingsComponent;
  let fixture: ComponentFixture<GitBackupSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GitBackupSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GitBackupSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
