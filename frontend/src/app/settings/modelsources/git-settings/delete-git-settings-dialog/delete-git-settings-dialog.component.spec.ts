import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteGitSettingsDialogComponent } from './delete-git-settings-dialog.component';

describe('DeleteGitSettingsDialogComponent', () => {
  let component: DeleteGitSettingsDialogComponent;
  let fixture: ComponentFixture<DeleteGitSettingsDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeleteGitSettingsDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DeleteGitSettingsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
