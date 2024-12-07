/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { DOCS_URL } from 'src/app/environment';
import { MetadataService } from '../metadata.service';

@Component({
  selector: 'app-version',
  templateUrl: './version.component.html',
  imports: [MatIcon, AsyncPipe],
})
export class VersionComponent {
  constructor(
    public metadataService: MetadataService,
    public dialog: MatDialog,
  ) {}

  get docsURL() {
    return DOCS_URL;
  }
}
