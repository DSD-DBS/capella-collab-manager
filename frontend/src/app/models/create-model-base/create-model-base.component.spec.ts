// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateModelBaseComponent } from './create-model-base.component';

describe('CreateModelBaseComponent', () => {
  let component: CreateModelBaseComponent;
  let fixture: ComponentFixture<CreateModelBaseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreateModelBaseComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateModelBaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
