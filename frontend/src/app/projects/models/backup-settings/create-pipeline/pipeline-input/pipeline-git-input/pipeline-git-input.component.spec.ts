/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PipelineGitInputComponent } from './pipeline-git-input.component';

describe('PipelineGitInputComponent', () => {
  let component: PipelineGitInputComponent;
  let fixture: ComponentFixture<PipelineGitInputComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PipelineGitInputComponent],
    });
    fixture = TestBed.createComponent(PipelineGitInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
