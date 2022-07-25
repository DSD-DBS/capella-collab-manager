// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SessionProgressIconComponent } from './session-progress-icon.component';

describe('SessionProgressIconComponent', () => {
  let component: SessionProgressIconComponent;
  let fixture: ComponentFixture<SessionProgressIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [SessionProgressIconComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SessionProgressIconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
