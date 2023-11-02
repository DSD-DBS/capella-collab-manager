/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PipelineEnvironmentInputComponent } from './pipeline-environment-input.component';

describe('PipelineEnvironmentInputComponent', () => {
  let component: PipelineEnvironmentInputComponent;
  let fixture: ComponentFixture<PipelineEnvironmentInputComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PipelineEnvironmentInputComponent],
    });
    fixture = TestBed.createComponent(PipelineEnvironmentInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
