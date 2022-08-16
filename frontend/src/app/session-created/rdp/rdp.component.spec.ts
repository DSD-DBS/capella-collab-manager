// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RDPComponent } from './rdp.component';

describe('RDPComponent', () => {
  let component: RDPComponent;
  let fixture: ComponentFixture<RDPComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [RDPComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RDPComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
