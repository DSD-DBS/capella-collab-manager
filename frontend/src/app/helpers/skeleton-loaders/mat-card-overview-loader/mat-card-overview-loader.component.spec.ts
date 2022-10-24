/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MatCardOverviewLoaderComponent } from './mat-card-overview-loader.component';

xdescribe('MatCardOverviewLoaderComponent', () => {
  let component: MatCardOverviewLoaderComponent;
  let fixture: ComponentFixture<MatCardOverviewLoaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [MatCardOverviewLoaderComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(MatCardOverviewLoaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
