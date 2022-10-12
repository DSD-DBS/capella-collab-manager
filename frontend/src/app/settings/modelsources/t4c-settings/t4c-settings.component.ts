/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import {
  T4CInstance,
  T4CInstanceService,
} from '../../../services/settings/t4c-model.service';

@Component({
  selector: 'app-t4c-settings',
  templateUrl: './t4c-settings.component.html',
  styleUrls: ['./t4c-settings.component.css'],
})
export class T4CSettingsComponent implements OnInit {
  _instances = new BehaviorSubject<T4CInstance[] | undefined>(undefined);
  get instances() {
    return this._instances.value;
  }

  constructor(
    private navbarService: NavBarService,
    private t4CInstanceService: T4CInstanceService
  ) {
    this.navbarService.title = 'Settings / Modelsources / T4C';
  }

  ngOnInit(): void {
    this.t4CInstanceService.listInstances().subscribe((res) => {
      this._instances.next(res);
    });
  }
}
