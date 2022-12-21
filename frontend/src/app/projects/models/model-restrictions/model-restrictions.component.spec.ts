/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ModelRestrictionsComponent } from './model-restrictions.component';

describe('ModelRestrictionsComponent', () => {
  let component: ModelRestrictionsComponent;
  let fixture: ComponentFixture<ModelRestrictionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ModelRestrictionsComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ModelRestrictionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
