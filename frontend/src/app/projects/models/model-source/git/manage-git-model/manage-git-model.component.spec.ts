/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageGitModelComponent } from './manage-git-model.component';

xdescribe('ManageGitModelComponent', () => {
  let component: ManageGitModelComponent;
  let fixture: ComponentFixture<ManageGitModelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ManageGitModelComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ManageGitModelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
