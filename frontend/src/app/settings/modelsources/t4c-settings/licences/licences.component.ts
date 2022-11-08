/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, Input } from '@angular/core';
import { SessionUsage } from 'src/app/schemes';
import {
  T4CInstance,
  T4CInstanceService,
} from 'src/app/services/settings/t4c-instance.service';

@Component({
  selector: 'app-licences',
  templateUrl: './licences.component.html',
  styleUrls: ['./licences.component.css'],
})
export class LicencesComponent implements OnInit {
  @Input() instance!: T4CInstance;

  public errorMessage?: string;

  constructor(private t4cInstanceService: T4CInstanceService) {}

  ngOnInit(): void {
    this.t4cInstanceService.getLicenses(this.instance.id).subscribe({
      next: (res) => {
        this.sessionUsage = res;
      },
      error: (err: HttpErrorResponse) => {
        this.errorMessage = err.error.detail.reason;
      },
    });
  }

  sessionUsage?: SessionUsage;
}
