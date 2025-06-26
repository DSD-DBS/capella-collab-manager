/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ChangeDetectionStrategy, Component, input } from '@angular/core';
import { MatRipple } from '@angular/material/core';
import { RouterLink } from '@angular/router';
import { MatIconComponent } from 'src/app/helpers/mat-icon/mat-icon.component';

@Component({
  selector: 'app-option-card',
  imports: [RouterLink, MatRipple, MatIconComponent],
  templateUrl: './option-card.component.html',
  styles: `
    :host {
      display: block;
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OptionCardComponent {
  routerLink = input.required<string[]>();
  name = input.required<string>();
  icon = input.required<string>();
}
