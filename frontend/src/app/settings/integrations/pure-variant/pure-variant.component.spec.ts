/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PureVariantComponent } from './pure-variant.component';

xdescribe('PureVariantComponent', () => {
  let component: PureVariantComponent;
  let fixture: ComponentFixture<PureVariantComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [PureVariantComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PureVariantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
