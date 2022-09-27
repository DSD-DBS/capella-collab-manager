/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */


import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelOverviewComponent } from './model-overview.component';

describe('ModelOverviewComponent', () => {
  let component: ModelOverviewComponent;
  let fixture: ComponentFixture<ModelOverviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ModelOverviewComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ModelOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
