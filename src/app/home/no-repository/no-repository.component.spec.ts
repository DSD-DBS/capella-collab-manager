import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NoRepositoryComponent } from './no-repository.component';

describe('NoRepositoryComponent', () => {
  let component: NoRepositoryComponent;
  let fixture: ComponentFixture<NoRepositoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ NoRepositoryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(NoRepositoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
