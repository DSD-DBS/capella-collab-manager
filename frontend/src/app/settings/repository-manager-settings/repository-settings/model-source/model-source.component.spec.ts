import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelSourceComponent } from './model-source.component';

describe('ModelSourceComponent', () => {
  let component: ModelSourceComponent;
  let fixture: ComponentFixture<ModelSourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ModelSourceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ModelSourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
