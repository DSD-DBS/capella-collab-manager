/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, inject } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { RelativeTimeComponent } from '../../../relative-time/relative-time.component';
import { VersionService } from '../version.service';

@Component({
  selector: 'app-version-dialog',
  imports: [MatIcon, RelativeTimeComponent],
  templateUrl: './version-dialog.component.html',
})
export class VersionDialogComponent {
  public versionService = inject(VersionService);
  protected readonly Date = Date;
}
