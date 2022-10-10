/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditT4CInstanceComponent } from './edit-t4c-instance.component';

describe('CreateT4cInstanceComponent', () => {
  let component: EditT4CInstanceComponent;
  let fixture: ComponentFixture<EditT4CInstanceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [EditT4CInstanceComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EditT4CInstanceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
