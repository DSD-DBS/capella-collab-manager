/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditT4cSourceComponent } from './edit-t4c-source.component';

describe('EditT4cSourceComponent', () => {
  let component: EditT4cSourceComponent;
  let fixture: ComponentFixture<EditT4cSourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EditT4cSourceComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EditT4cSourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
