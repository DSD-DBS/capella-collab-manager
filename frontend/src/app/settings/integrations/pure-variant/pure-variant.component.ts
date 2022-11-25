/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { filter } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { PureVariantService } from 'src/app/services/pure-variant/pure-variant.service';

@Component({
  selector: 'app-pure-variant',
  templateUrl: './pure-variant.component.html',
  styleUrls: ['./pure-variant.component.css'],
})
export class PureVariantComponent implements OnInit {
  form = new FormGroup({
    value: new FormControl<string>('', Validators.pattern(/^https?:\/\//)),
  });

  constructor(
    private pureVariantService: PureVariantService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.pureVariantService
      .get_license()
      .pipe(filter(Boolean))
      .subscribe((res) => {
        this.form.controls.value.patchValue(res.value);
      });
  }

  onSubmit(): void {
    this.pureVariantService
      .set_license(this.form.value.value!)
      .subscribe((res) => {
        this.toastService.showSuccess(
          'Floating license server updating.',
          'The floating license server was updated.'
        );
        this.form.controls.value.patchValue(res.value);
      });
  }
}
