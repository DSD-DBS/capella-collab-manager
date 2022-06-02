import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteRepositoryComponent } from './delete-repository.component';

describe('CreateRepositoryComponent', () => {
  let component: DeleteRepositoryComponent;
  let fixture: ComponentFixture<DeleteRepositoryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeleteRepositoryComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DeleteRepositoryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should delete', () => {
    expect(component).toBeTruthy();
  });
});
