/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Input } from '@angular/core';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';

@Component({
  selector: 'app-button-skeleton-loader',
  templateUrl: './button-skeleton-loader.component.html',
  standalone: true,
  imports: [NgxSkeletonLoaderModule],
})
export class ButtonSkeletonLoaderComponent {
  @Input() loading = true;
}
