import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GuacamoleComponent } from './guacamole.component';

describe('GuacamoleComponent', () => {
  let component: GuacamoleComponent;
  let fixture: ComponentFixture<GuacamoleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GuacamoleComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GuacamoleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
