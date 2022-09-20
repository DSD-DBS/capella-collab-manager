/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChooseInitComponent } from './choose-init.component';

xdescribe('ChooseInitComponent', () => {
  let component: ChooseInitComponent;
  let fixture: ComponentFixture<ChooseInitComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ChooseInitComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ChooseInitComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
