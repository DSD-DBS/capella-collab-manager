/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgIf, AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { environment } from 'src/environments/environment';
import { MetadataService } from '../metadata.service';

@Component({
  selector: 'app-version',
  templateUrl: './version.component.html',
  standalone: true,
  imports: [NgIf, MatIcon, AsyncPipe],
})
export class VersionComponent {
  constructor(
    public metadataService: MetadataService,
    public dialog: MatDialog,
  ) {}

  get docsURL() {
    return environment.docs_url;
  }
}
