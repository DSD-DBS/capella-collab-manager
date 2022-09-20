/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateCoworkingMethodComponent } from './create-coworking-method.component';

describe('CreateCoworkingMethodComponent', () => {
  let component: CreateCoworkingMethodComponent;
  let fixture: ComponentFixture<CreateCoworkingMethodComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreateCoworkingMethodComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateCoworkingMethodComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
