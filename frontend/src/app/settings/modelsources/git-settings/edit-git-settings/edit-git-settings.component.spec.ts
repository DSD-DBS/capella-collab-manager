/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */


import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditGitSettingsComponent } from './edit-git-settings.component';

describe('EditGitSettingsComponent', () => {
  let component: EditGitSettingsComponent;
  let fixture: ComponentFixture<EditGitSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EditGitSettingsComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EditGitSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
