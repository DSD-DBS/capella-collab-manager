/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateT4CInstanceComponent } from './create-t4c-instance.component';

describe('CreateT4cInstanceComponent', () => {
  let component: CreateT4CInstanceComponent;
  let fixture: ComponentFixture<CreateT4CInstanceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreateT4CInstanceComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateT4CInstanceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
