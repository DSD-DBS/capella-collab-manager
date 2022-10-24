/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ToolVersionComponent } from './tool-version.component';

xdescribe('ToolVersionComponent', () => {
  let component: ToolVersionComponent;
  let fixture: ComponentFixture<ToolVersionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ToolVersionComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ToolVersionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
