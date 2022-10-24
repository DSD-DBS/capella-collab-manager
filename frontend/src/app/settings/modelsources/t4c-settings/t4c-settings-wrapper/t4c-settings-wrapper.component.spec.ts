/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { T4CSettingsWrapperComponent } from './t4c-settings-wrapper.component';

xdescribe('T4cSettingsWrapperComponent', () => {
  let component: T4CSettingsWrapperComponent;
  let fixture: ComponentFixture<T4CSettingsWrapperComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [T4CSettingsWrapperComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(T4CSettingsWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
