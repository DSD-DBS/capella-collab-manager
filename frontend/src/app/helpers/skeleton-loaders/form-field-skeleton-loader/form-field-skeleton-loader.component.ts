/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component } from '@angular/core';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'app-form-field-skeleton-loader',
  templateUrl: './form-field-skeleton-loader.component.html',
  imports: [NgxSkeletonLoaderModule],
})
export class FormFieldSkeletonLoaderComponent {}
