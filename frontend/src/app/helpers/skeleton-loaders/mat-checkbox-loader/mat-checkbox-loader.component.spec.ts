/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatCheckboxLoaderComponent } from './mat-checkbox-loader.component';

describe('MatCheckboxLoaderComponent', () => {
  let component: MatCheckboxLoaderComponent;
  let fixture: ComponentFixture<MatCheckboxLoaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MatCheckboxLoaderComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MatCheckboxLoaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
