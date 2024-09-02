/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgFor, NgClass, NgIf, AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { MatRipple } from '@angular/material/core';
import { MatIcon } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import { MatIconComponent } from '../../../helpers/mat-icon/mat-icon.component';

@Component({
  selector: 'app-t4c-settings',
  templateUrl: './t4c-settings.component.html',
  styleUrls: ['./t4c-settings.component.css'],
  standalone: true,
  imports: [
    RouterLink,
    MatRipple,
    MatIconComponent,
    NgFor,
    NgClass,
    MatIcon,
    NgIf,
    AsyncPipe,
  ],
})
export class T4CSettingsComponent {
  constructor(public t4cInstanceService: T4CInstanceWrapperService) {}
}
