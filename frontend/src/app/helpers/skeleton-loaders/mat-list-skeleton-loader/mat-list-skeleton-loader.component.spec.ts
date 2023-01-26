/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatListSkeletonLoaderComponent } from './mat-list-skeleton-loader.component';

describe('MatListSkeletonLoaderComponent', () => {
  let component: MatListSkeletonLoaderComponent;
  let fixture: ComponentFixture<MatListSkeletonLoaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MatListSkeletonLoaderComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MatListSkeletonLoaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
