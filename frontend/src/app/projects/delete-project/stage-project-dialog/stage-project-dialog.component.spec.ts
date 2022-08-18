import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StageProjectDialogComponent } from './stage-project-dialog.component';

describe('StageProjectDialogComponent', () => {
  let component: StageProjectDialogComponent;
  let fixture: ComponentFixture<StageProjectDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [StageProjectDialogComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StageProjectDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
