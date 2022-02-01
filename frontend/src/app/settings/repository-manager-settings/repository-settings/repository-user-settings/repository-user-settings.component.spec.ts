import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RepositoryUserSettingsComponent } from './repository-user-settings.component';

describe('RepositoryUserSettingsComponent', () => {
  let component: RepositoryUserSettingsComponent;
  let fixture: ComponentFixture<RepositoryUserSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RepositoryUserSettingsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RepositoryUserSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
