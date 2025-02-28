/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe, NgClass } from '@angular/common';
import { Component, inject } from '@angular/core';
import { NavBarService } from '../nav-bar/nav-bar.service';
import { SpecialService } from '../special-service/special.service';

@Component({
  selector: 'app-logo',
  standalone: true,
  templateUrl: './logo.component.html',
  imports: [AsyncPipe, NgClass],
})
export class LogoComponent {
  public navBarService = inject(NavBarService);
  public specialService = inject(SpecialService);
}
