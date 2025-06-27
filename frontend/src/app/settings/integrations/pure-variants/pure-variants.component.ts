/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, OnInit, inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatInput } from '@angular/material/input';
import { filter, finalize, switchMap, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  IntegrationsPureVariantsService,
  PureVariantsLicensesOutput,
} from 'src/app/openapi';
import { FormFieldSkeletonLoaderComponent } from '../../../helpers/skeleton-loaders/form-field-skeleton-loader/form-field-skeleton-loader.component';

@Component({
  selector: 'app-pure-variants',
  templateUrl: './pure-variants.component.html',
  styleUrls: ['./pure-variants.component.css'],
  imports: [
    FormsModule,
    ReactiveFormsModule,
    FormFieldSkeletonLoaderComponent,
    MatFormField,
    MatLabel,
    MatInput,
    MatButton,
  ],
})
export class PureVariantsComponent implements OnInit {
  private pureVariantsService = inject(IntegrationsPureVariantsService);
  private toastService = inject(ToastService);

  configuration?: PureVariantsLicensesOutput = undefined;
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

  ngOnInit(): void {
    this.pureVariantsService
      .getLicense()
      .pipe(
        tap((res) => (this.configuration = res)),
        filter(Boolean),
      )
      .subscribe((res) => {
        this.licenseServerConfigurationForm.controls.licenseServerURL.patchValue(
          res.license_server_url || '',
        );
      });
  }

  onLicenseConfigurationSubmit(): void {
    this.loading = true;
    this.pureVariantsService
      .setLicense({
        license_server_url:
          this.licenseServerConfigurationForm.value.licenseServerURL!,
      })
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

    this.pureVariantsService
      .uploadLicenseKeyFile(
        this.licenseKeyUploadForm.controls.licenseFile.value!,
      )
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
      .deleteLicenseKeyFile()
      .pipe(
        switchMap(() => this.pureVariantsService.getLicense()),
        finalize(() => {
          this.loadingLicenseKey = false;
        }),
      )
      .subscribe((res) => {
        this.configuration = res;
      });
  }
}
