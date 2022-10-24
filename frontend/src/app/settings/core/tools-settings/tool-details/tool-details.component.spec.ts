/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ToolDetailsComponent } from './tool-details.component';

xdescribe('ToolDetailsComponent', () => {
  let component: ToolDetailsComponent;
  let fixture: ComponentFixture<ToolDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ToolDetailsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ToolDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
