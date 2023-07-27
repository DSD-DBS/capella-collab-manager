/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WorkspaceOverviewComponent } from './workspace-overview.component';

describe('WorkspaceOverviewComponent', () => {
  let component: WorkspaceOverviewComponent;
  let fixture: ComponentFixture<WorkspaceOverviewComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [WorkspaceOverviewComponent],
    });
    fixture = TestBed.createComponent(WorkspaceOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
