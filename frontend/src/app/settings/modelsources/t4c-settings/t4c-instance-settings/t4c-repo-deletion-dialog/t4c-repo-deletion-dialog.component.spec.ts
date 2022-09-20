/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { T4CRepoDeletionDialogComponent } from './t4c-repo-deletion-dialog.component';

xdescribe('T4CRepoDeletionDialogComponent', () => {
  let component: T4CRepoDeletionDialogComponent;
  let fixture: ComponentFixture<T4CRepoDeletionDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [T4CRepoDeletionDialogComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(T4CRepoDeletionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
