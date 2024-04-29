/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MetadataService } from 'src/app/general/metadata/metadata.service';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css'],
  standalone: true,
  imports: [AsyncPipe],
})
export class FooterComponent {
  constructor(
    public dialog: MatDialog,
    public metadataService: MetadataService,
  ) {}
}
