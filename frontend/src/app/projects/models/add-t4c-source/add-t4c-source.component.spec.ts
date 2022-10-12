/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddT4cSourceComponent } from './add-t4c-source.component';

describe('AddT4cSourceComponent', () => {
  let component: AddT4cSourceComponent;
  let fixture: ComponentFixture<AddT4cSourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AddT4cSourceComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AddT4cSourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
