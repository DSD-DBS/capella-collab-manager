/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, Input } from '@angular/core';
import { GetSessionUsageResponse, T4CInstance } from 'src/app/openapi';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';

@Component({
  selector: 'app-licences',
  templateUrl: './licences.component.html',
  styleUrls: ['./licences.component.css'],
  standalone: true,
  imports: [NgIf],
})
export class LicencesComponent implements OnInit {
  @Input() instance!: T4CInstance;

  public errorMessage?: string;

  constructor(private t4cInstanceService: T4CInstanceWrapperService) {}

  ngOnInit(): void {
    this.t4cInstanceService.getLicenses(this.instance.id).subscribe({
      next: (res) => {
        this.sessionUsage = res;
      },
      error: (err: HttpErrorResponse) => {
        this.errorMessage =
          err.error.detail.reason ||
          'Unknown error. Please contact your system administrator.';
      },
    });
  }

  sessionUsage?: GetSessionUsageResponse;
}
