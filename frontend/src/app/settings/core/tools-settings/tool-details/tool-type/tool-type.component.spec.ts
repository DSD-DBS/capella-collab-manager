/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ToolTypeComponent } from './tool-type.component';

describe('ToolTypeComponent', () => {
  let component: ToolTypeComponent;
  let fixture: ComponentFixture<ToolTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ToolTypeComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ToolTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
