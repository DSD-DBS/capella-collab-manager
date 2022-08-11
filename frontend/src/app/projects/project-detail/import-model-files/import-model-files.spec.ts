// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateModelComponent } from './import-model-files';

describe('CreateModelComponent', () => {
  let component: CreateModelComponent;
  let fixture: ComponentFixture<CreateModelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreateModelComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateModelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
