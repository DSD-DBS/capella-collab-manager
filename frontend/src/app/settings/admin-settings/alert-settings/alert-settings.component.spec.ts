import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlertSettingsComponent } from './alert-settings.component';

describe('AlertSettingsComponent', () => {
  let component: AlertSettingsComponent;
  let fixture: ComponentFixture<AlertSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AlertSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AlertSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
