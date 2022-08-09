import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FileExistsDialogComponent } from './file-exists-dialog.component';

describe('FileExistsDialogComponent', () => {
  let component: FileExistsDialogComponent;
  let fixture: ComponentFixture<FileExistsDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FileExistsDialogComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(FileExistsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
