/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { T4CSettingsComponent } from './t4c-settings.component';

xdescribe('T4CSettingsComponent', () => {
  let component: T4CSettingsComponent;
  let fixture: ComponentFixture<T4CSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [T4CSettingsComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(T4CSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
