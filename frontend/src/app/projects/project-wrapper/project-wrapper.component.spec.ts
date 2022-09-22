/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProjectWrapperComponent } from './project-wrapper.component';

xdescribe('ProjectWrapperComponent', () => {
  let component: ProjectWrapperComponent;
  let fixture: ComponentFixture<ProjectWrapperComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ProjectWrapperComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProjectWrapperComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
