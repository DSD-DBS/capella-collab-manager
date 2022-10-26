/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { T4cModelWrapperComponent } from './t4c-model-wrapper.component';

xdescribe('T4cModelWrapperComponent', () => {
  let component: T4cModelWrapperComponent;
  let fixture: ComponentFixture<T4cModelWrapperComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [T4cModelWrapperComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(T4cModelWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
