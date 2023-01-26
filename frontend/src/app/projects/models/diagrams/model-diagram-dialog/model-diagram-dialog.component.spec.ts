/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelDiagramDialogComponent } from './model-diagram-dialog.component';

describe('ModelDiagramDialogComponent', () => {
  let component: ModelDiagramDialogComponent;
  let fixture: ComponentFixture<ModelDiagramDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ModelDiagramDialogComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ModelDiagramDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
