/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PipelineT4CInputComponent } from './pipeline-t4c-input.component';

describe('PipelineT4cInputComponent', () => {
  let component: PipelineT4CInputComponent;
  let fixture: ComponentFixture<PipelineT4CInputComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PipelineT4CInputComponent],
    });
    fixture = TestBed.createComponent(PipelineT4CInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
