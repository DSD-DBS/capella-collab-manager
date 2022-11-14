/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TriggerPipelineComponent } from './trigger-pipeline.component';

xdescribe('TriggerPipelineComponent', () => {
  let component: TriggerPipelineComponent;
  let fixture: ComponentFixture<TriggerPipelineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [TriggerPipelineComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TriggerPipelineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
