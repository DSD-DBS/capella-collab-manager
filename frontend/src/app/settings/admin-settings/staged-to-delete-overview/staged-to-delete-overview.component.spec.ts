import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StagedToDeleteOverviewComponent } from './staged-to-delete-overview.component';

describe('StagedToDeleteOverviewComponent', () => {
  let component: StagedToDeleteOverviewComponent;
  let fixture: ComponentFixture<StagedToDeleteOverviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ StagedToDeleteOverviewComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StagedToDeleteOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
