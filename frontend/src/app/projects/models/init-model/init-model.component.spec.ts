/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InitModelComponent } from './init-model.component';

describe('InitModelComponent', () => {
  let component: InitModelComponent;
  let fixture: ComponentFixture<InitModelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [InitModelComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(InitModelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
