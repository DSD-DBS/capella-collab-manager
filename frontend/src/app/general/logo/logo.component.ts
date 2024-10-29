/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import { Component } from '@angular/core';
import { NavBarService } from '../nav-bar/nav-bar.service';

@Component({
  selector: 'app-logo',
  standalone: true,
  templateUrl: './logo.component.html',
  imports: [AsyncPipe],
})
export class LogoComponent {
  constructor(public navBarService: NavBarService) {}
}
