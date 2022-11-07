/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  BackupSettings,
  BackupSettingsService,
} from '../service/backup-settings.service';

@Component({
  selector: 'app-t4c-importer-settings',
  templateUrl: './t4c-importer-settings.component.html',
  styleUrls: ['./t4c-importer-settings.component.css'],
})
export class T4CImporterSettingsComponent implements OnInit {
  editing = false;

  t4cImporterSettingsForm = new FormGroup({
    dockerImage: new FormControl('', Validators.required),
  });

  constructor(
    private backupSettingsService: BackupSettingsService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.backupSettingsService
      .getBackupSettings()
      .subscribe(this.updateForm.bind(this));
    this.disableEditing();
  }

  updateForm(backupSettings: BackupSettings) {
    this.t4cImporterSettingsForm.controls.dockerImage.patchValue(
      backupSettings.docker_image
    );
  }

  enableEditing(): void {
    this.editing = true;
    this.t4cImporterSettingsForm.enable();
  }

  disableEditing(): void {
    this.editing = false;
    this.t4cImporterSettingsForm.disable();
  }

  updateBackupSettings(): void {
    if (this.t4cImporterSettingsForm.valid) {
      this.backupSettingsService
        .updateBackupSettings({
          docker_image: this.t4cImporterSettingsForm.value.dockerImage!,
        })
        .subscribe(() => {
          this.disableEditing();
          this.toastService.showSuccess(
            'Backup settings updated',
            'The backup settings were updated successfully.'
          );
        });
    }
  }
}
