/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ToolNatureComponent } from './tool-nature.component';

xdescribe('ToolNatureComponent', () => {
  let component: ToolNatureComponent;
  let fixture: ComponentFixture<ToolNatureComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ToolNatureComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ToolNatureComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
