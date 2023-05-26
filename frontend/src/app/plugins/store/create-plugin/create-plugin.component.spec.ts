/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreatePluginComponent } from './create-plugin.component';

describe('CreatePluginComponent', () => {
  let component: CreatePluginComponent;
  let fixture: ComponentFixture<CreatePluginComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [CreatePluginComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CreatePluginComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
