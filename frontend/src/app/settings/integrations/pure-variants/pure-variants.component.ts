/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { filter, finalize, switchMap, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  PureVariantsConfiguration,
  PureVariantsService,
} from 'src/app/settings/integrations/pure-variants/service/pure-variants.service';

@Component({
  selector: 'app-pure-variants',
  templateUrl: './pure-variants.component.html',
  styleUrls: ['./pure-variants.component.css'],
})
export class PureVariantsComponent implements OnInit {
  configuration?: PureVariantsConfiguration = undefined;
  loading = false;
  loadingLicenseKey = false;

  licenseServerConfigurationForm = new FormGroup({
    licenseServerURL: new FormControl<string>(
      '',
      Validators.pattern(/^https?:\/\//),
    ),
  });

  licenseKeyUploadForm = new FormGroup({
    licenseFileName: new FormControl('', Validators.required),
    licenseFile: new FormControl<File | null>(null, Validators.required),
  });

  get selectedFile() {
    const value = this.licenseKeyUploadForm.controls.licenseFileName.value;
    if (value) {
      return value.substring(value.lastIndexOf('\\') + 1);
    }
    return null;
  }

  onLicenseFileChange($event: Event) {
    const inputElement = $event.target as HTMLInputElement;
    if (inputElement.files) {
      this.licenseKeyUploadForm.patchValue({
        licenseFile: inputElement.files[0],
      });
    }
  }

  constructor(
    private pureVariantsService: PureVariantsService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.pureVariantsService
      .getLicenseServerConfiguration()
      .pipe(
        tap((res: PureVariantsConfiguration) => (this.configuration = res)),
        filter(Boolean),
      )
      .subscribe((res: PureVariantsConfiguration) => {
        this.licenseServerConfigurationForm.controls.licenseServerURL.patchValue(
          res.license_server_url || '',
        );
      });
  }

  onLicenseConfigurationSubmit(): void {
    this.loading = true;
    this.pureVariantsService
      .setLicenseServerURL(
        this.licenseServerConfigurationForm.value.licenseServerURL!,
      )
      .pipe(
        finalize(() => {
          this.loading = false;
        }),
      )
      .subscribe((res) => {
        this.configuration = res;
        this.toastService.showSuccess(
          'pure::variants configuration changed',
          `The floating license server was updated to "${res.license_server_url}"`,
        );
        this.licenseServerConfigurationForm.controls.licenseServerURL.patchValue(
          res.license_server_url!,
        );
      });
  }

  onLicenseFileUploadSubmit(): void {
    this.loadingLicenseKey = true;

    const formData = new FormData();
    formData.append(
      'file',
      this.licenseKeyUploadForm.controls.licenseFile.value!,
      this.selectedFile!,
    );

    this.pureVariantsService
      .uploadLicenseServerFile(formData)
      .pipe(
        finalize(() => {
          this.loadingLicenseKey = false;
        }),
      )
      .subscribe((res) => {
        this.configuration = res;
        this.toastService.showSuccess(
          'pure::variants license key upload successful',
          `The license key will be injected in all future sessions which are linked to the pure::variants server`,
        );
      });
  }

  onLicenseFileDeletionClick(): void {
    this.loadingLicenseKey = true;
    this.pureVariantsService
      .deleteLicenseServerFile()
      .pipe(
        switchMap(() =>
          this.pureVariantsService.getLicenseServerConfiguration(),
        ),
        finalize(() => {
          this.loadingLicenseKey = false;
        }),
      )
      .subscribe((res: PureVariantsConfiguration) => {
        this.configuration = res;
      });
  }
}
