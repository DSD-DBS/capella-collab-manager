/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';
import { LocalStorageService } from 'src/app/general/auth/local-storage/local-storage.service';
import { Session } from 'src/app/schemes';
import { GuacamoleService } from 'src/app/services/guacamole/guacamole.service';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-guacamole',
  templateUrl: './guacamole.component.html',
  styleUrls: ['./guacamole.component.css'],
})
export class GuacamoleComponent {
  @Input()
  session: Session | undefined = undefined;

  constructor(
    public userService: UserService,
    private localStorageService: LocalStorageService,
    private guacamoleService: GuacamoleService
  ) {}

  redirectToGuacamole(): void {
    this.guacamoleService
      .getGucamoleToken(this.session?.id || '')
      .subscribe((res) => {
        this.localStorageService.setValue('GUAC_AUTH', res.token);
        window.open(res.url);
      });
  }
}
