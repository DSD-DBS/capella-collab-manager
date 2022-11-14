/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateBackupComponent } from '../create-backup/create-backup.component';

xdescribe('CreateGitBackupComponent', () => {
  let component: CreateBackupComponent;
  let fixture: ComponentFixture<CreateBackupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreateBackupComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateBackupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
