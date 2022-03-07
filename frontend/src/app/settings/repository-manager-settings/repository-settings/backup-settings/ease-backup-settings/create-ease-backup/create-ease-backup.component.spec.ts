import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateEASEBackupComponent } from './create-ease-backup.component';

describe('CreateGitBackupComponent', () => {
  let component: CreateEASEBackupComponent;
  let fixture: ComponentFixture<CreateEASEBackupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreateEASEBackupComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateEASEBackupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
