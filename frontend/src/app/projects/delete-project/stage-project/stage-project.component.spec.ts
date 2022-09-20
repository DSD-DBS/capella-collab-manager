/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StageProjectComponent } from './stage-project.component';

describe('StageProjectComponent', () => {
  let component: StageProjectComponent;
  let fixture: ComponentFixture<StageProjectComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [StageProjectComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(StageProjectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
