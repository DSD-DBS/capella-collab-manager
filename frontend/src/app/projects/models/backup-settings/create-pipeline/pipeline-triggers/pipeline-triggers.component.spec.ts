/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PipelineTriggersComponent } from './pipeline-triggers.component';

describe('PipelineTriggersComponent', () => {
  let component: PipelineTriggersComponent;
  let fixture: ComponentFixture<PipelineTriggersComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PipelineTriggersComponent],
    });
    fixture = TestBed.createComponent(PipelineTriggersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
