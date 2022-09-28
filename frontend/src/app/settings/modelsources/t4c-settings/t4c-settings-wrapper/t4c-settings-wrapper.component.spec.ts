/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { T4cSettingsWrapperComponent } from './t4c-settings-wrapper.component';

describe('T4cSettingsWrapperComponent', () => {
  let component: T4cSettingsWrapperComponent;
  let fixture: ComponentFixture<T4cSettingsWrapperComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [T4cSettingsWrapperComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(T4cSettingsWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
