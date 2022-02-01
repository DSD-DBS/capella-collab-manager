import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RequestSessionComponent } from './request-session.component';

describe('RequestSessionComponent', () => {
  let component: RequestSessionComponent;
  let fixture: ComponentFixture<RequestSessionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RequestSessionComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RequestSessionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
