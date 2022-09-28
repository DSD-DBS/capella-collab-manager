/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateT4cInstanceComponent } from './create-t4c-instance.component';

describe('CreateT4cInstanceComponent', () => {
  let component: CreateT4cInstanceComponent;
  let fixture: ComponentFixture<CreateT4cInstanceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreateT4cInstanceComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateT4cInstanceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
