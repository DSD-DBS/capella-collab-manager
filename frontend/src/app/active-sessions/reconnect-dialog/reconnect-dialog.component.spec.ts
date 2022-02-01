import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReconnectDialogComponent } from './reconnect-dialog.component';

describe('ReconnectDialogComponent', () => {
  let component: ReconnectDialogComponent;
  let fixture: ComponentFixture<ReconnectDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ReconnectDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ReconnectDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
