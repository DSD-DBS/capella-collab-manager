/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JenkinsBackupSettingsComponent } from './jenkins-backup-settings.component';

describe('JenkinsBackupSettingsComponent', () => {
  let component: JenkinsBackupSettingsComponent;
  let fixture: ComponentFixture<JenkinsBackupSettingsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [JenkinsBackupSettingsComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(JenkinsBackupSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
