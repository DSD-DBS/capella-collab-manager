import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RepositorySyncSettingsComponent } from './repository-sync-settings.component';

describe('RepositorySyncSettingsComponent', () => {
  let component: RepositorySyncSettingsComponent;
  let fixture: ComponentFixture<RepositorySyncSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RepositorySyncSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RepositorySyncSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
