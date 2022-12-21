/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddGitSourceComponent } from './add-git-source.component';

xdescribe('AddGitSourceComponent', () => {
  let component: AddGitSourceComponent;
  let fixture: ComponentFixture<AddGitSourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [AddGitSourceComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AddGitSourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});