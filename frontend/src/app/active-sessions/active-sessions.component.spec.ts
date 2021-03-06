// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ActiveSessionsComponent } from './active-sessions.component';

describe('ActiveSessionsComponent', () => {
  let component: ActiveSessionsComponent;
  let fixture: ComponentFixture<ActiveSessionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ActiveSessionsComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ActiveSessionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
