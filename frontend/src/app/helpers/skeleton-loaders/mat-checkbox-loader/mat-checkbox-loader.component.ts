/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component } from '@angular/core';
import { MatProgressSpinner } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-mat-checkbox-loader',
  templateUrl: './mat-checkbox-loader.component.html',
  styleUrls: ['./mat-checkbox-loader.component.css'],
  imports: [MatProgressSpinner],
})
export class MatCheckboxLoaderComponent {}
