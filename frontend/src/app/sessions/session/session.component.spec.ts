/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SessionComponent } from './session.component';

describe('SessionComponent', () => {
  let component: SessionComponent;
  let fixture: ComponentFixture<SessionComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SessionComponent],
    });
    fixture = TestBed.createComponent(SessionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
