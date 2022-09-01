/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LicencesComponent } from './licences.component';

describe('LicencesComponent', () => {
  let component: LicencesComponent;
  let fixture: ComponentFixture<LicencesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [LicencesComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(LicencesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
