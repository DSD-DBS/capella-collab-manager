/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ManageT4CModelComponent } from '../manage-t4c-model/manage-t4c-model.component';

xdescribe('AddT4cSourceComponent', () => {
  let component: ManageT4CModelComponent;
  let fixture: ComponentFixture<ManageT4CModelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ManageT4CModelComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ManageT4CModelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
