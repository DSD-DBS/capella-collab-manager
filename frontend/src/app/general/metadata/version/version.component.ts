/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MetadataService } from '../metadata.service';

@Component({
  selector: 'app-version',
  templateUrl: './version.component.html',
})
export class VersionComponent {
  constructor(
    public metadataService: MetadataService,
    public dialog: MatDialog,
  ) {}
}
