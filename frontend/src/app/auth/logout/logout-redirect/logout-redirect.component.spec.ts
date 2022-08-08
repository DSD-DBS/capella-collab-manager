// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LogoutRedirectComponent } from './logout-redirect.component';

describe('LogoutRedirectComponent', () => {
  let component: LogoutRedirectComponent;
  let fixture: ComponentFixture<LogoutRedirectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LogoutRedirectComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LogoutRedirectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
