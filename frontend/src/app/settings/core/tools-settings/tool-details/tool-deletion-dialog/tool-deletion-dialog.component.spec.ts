/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ToolDeletionDialogComponent } from './tool-deletion-dialog.component';

xdescribe('ToolDeletionDialogComponent', () => {
  let component: ToolDeletionDialogComponent;
  let fixture: ComponentFixture<ToolDeletionDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ToolDeletionDialogComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ToolDeletionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
