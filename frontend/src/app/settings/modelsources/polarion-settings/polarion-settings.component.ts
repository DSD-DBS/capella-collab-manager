/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialog, MatDialogRef } from '@angular/material/dialog';
import { UntilDestroy } from '@ngneat/until-destroy';
import { absoluteUrlValidator } from 'src/app/helpers/validators/url-validator';
import { DeleteGitSettingsDialogComponent } from 'src/app/settings/modelsources/git-settings/delete-git-settings-dialog/delete-git-settings-dialog.component';
import {
  PolarionInstance,
  PolarionInstanceService,
} from 'src/app/settings/modelsources/polarion-settings/service/polarion-instance.service';

@UntilDestroy()
@Component({
  selector: 'app-polarion-settings',
  templateUrl: './polarion-settings.component.html',
})
export class PolarionSettingsComponent {
  constructor(
    public dialog: MatDialog,
    public dialogRef: MatDialogRef<DeleteGitSettingsDialogComponent>,
    public polarionInstanceService: PolarionInstanceService,
  ) {}

  ngOnInit(): void {
    this.polarionInstanceService.loadPolarionInstances();
  }

  polarionInstanceForm = new FormGroup({
    name: new FormControl('', {
      validators: Validators.required,
      //asyncValidators: true,
    }),
    url: new FormControl('', [Validators.required, absoluteUrlValidator()]),
  });

  createPolarionInstance(): void {
    if (this.polarionInstanceForm.valid) {
      let url = this.polarionInstanceForm.value.url!;
      if (url.endsWith('/')) {
        url = url.slice(0, -1);
      }
    }

    this.polarionInstanceService
      .createPolarionInstance(
        this.polarionInstanceForm.value as PolarionInstance,
      )
      .subscribe(() => this.polarionInstanceForm.reset());
  }

  deletePolarionInstance(polarionInstance: PolarionInstance) {}
}
