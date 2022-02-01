import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GitModelDeletionDialogComponent } from './git-model-deletion-dialog.component';

describe('GitModelDeletionDialogComponent', () => {
  let component: GitModelDeletionDialogComponent;
  let fixture: ComponentFixture<GitModelDeletionDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GitModelDeletionDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GitModelDeletionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
