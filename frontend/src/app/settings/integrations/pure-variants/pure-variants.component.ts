/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { filter } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { PureVariantsService } from 'src/app/settings/integrations/pure-variants/service/pure-variants.service';

@Component({
  selector: 'app-pure-variants',
  templateUrl: './pure-variants.component.html',
  styleUrls: ['./pure-variants.component.css'],
})
export class PureVariantsComponent implements OnInit {
  loading = true;

  form = new FormGroup({
    licenseServerURL: new FormControl<string>(
      '',
      Validators.pattern(/^https?:\/\//)
    ),
  });

  constructor(
    private pureVariantsService: PureVariantsService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.pureVariantsService
      .getLicenseServerURL()
      .pipe(filter(Boolean))
      .subscribe((res) => {
        this.loading = false;
        this.form.controls.licenseServerURL.patchValue(
          res.license_server_url || ''
        );
      });
  }

  onSubmit(): void {
    this.loading = true;
    this.pureVariantsService
      .setLicenseServerURL(this.form.value.licenseServerURL!)
      .subscribe((res) => {
        this.loading = false;
        this.toastService.showSuccess(
          'pure::variants configuration changed',
          `The floating license server was updated to "${res.license_server_url}"`
        );
        this.form.controls.licenseServerURL.patchValue(res.license_server_url!);
      });
  }
}
