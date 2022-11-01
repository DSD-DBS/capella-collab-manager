/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit, Input } from '@angular/core';
import { SessionUsage } from 'src/app/schemes';
import {
  T4CInstance,
  T4CInstanceService,
} from 'src/app/services/settings/t4c-model.service';

@Component({
  selector: 'app-licences',
  templateUrl: './licences.component.html',
  styleUrls: ['./licences.component.css'],
})
export class LicencesComponent implements OnInit {
  @Input() instance!: T4CInstance;

  constructor(private t4cInstanceService: T4CInstanceService) {}

  ngOnInit(): void {
    this.t4cInstanceService.getLicenses(this.instance.id).subscribe((res) => {
      this.sessionUsage = res;
    });
  }

  sessionUsage?: SessionUsage;

  getErrorMessage(error: string): string {
    switch (error) {
      case 'T4C_ERROR':
        return 'Internal server error in the license server.';
      case 'TIMEOUT':
        return 'The connection to the license server timed out.';
      case 'CONNECTION_ERROR':
        return 'The connection to the license server failed.';
      case 'NO_STATUS':
        return 'No status is available. This can happen during and after license server restarts.';
      case 'NO_STATUS_JSON':
        return 'No status in response from license server.';
      case 'UNKNOWN_ERROR':
        return 'An unknown error occured when communicating with the license server.';
      case 'DECODE_ERROR':
        return 'License server response could not be decoded.';
      default:
        return 'Unknown error. Please contact your system administrator.';
    }
  }
}
