/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf } from '@angular/common';
import { Component, Input } from '@angular/core';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'app-button-skeleton-loader',
  templateUrl: './button-skeleton-loader.component.html',
  styleUrls: ['./button-skeleton-loader.component.css'],
  standalone: true,
  imports: [NgIf, NgxSkeletonLoaderModule],
})
export class ButtonSkeletonLoaderComponent {
  @Input() loading = true;
}
