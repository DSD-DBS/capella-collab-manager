import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SessionCreationProgressComponent } from './session-creation-progress.component';

describe('SessionCreationProgressComponent', () => {
  let component: SessionCreationProgressComponent;
  let fixture: ComponentFixture<SessionCreationProgressComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SessionCreationProgressComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SessionCreationProgressComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
