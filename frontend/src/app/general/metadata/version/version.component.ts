/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatIcon } from '@angular/material/icon';
import { DOCS_URL } from 'src/app/environment';
import { VersionDialogComponent } from './version-dialog/version-dialog.component';
import { VersionService } from './version.service';

@Component({
  selector: 'app-version',
  templateUrl: './version.component.html',
  imports: [MatIcon],
})
export class VersionComponent {
  public versionService = inject(VersionService);
  constructor(public dialog: MatDialog) {}

  get docsURL() {
    return DOCS_URL;
  }

  openDialog() {
    this.dialog.open(VersionDialogComponent, { autoFocus: 'dialog' });
  }
}
