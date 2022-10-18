/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, OnInit } from '@angular/core';
import { UserService } from 'src/app/services/user/user.service';

@Component({
  selector: 'app-no-repository',
  templateUrl: './no-repository.component.html',
  styleUrls: ['./no-repository.component.css'],
})
export class NoRepositoryComponent {
  constructor(public userService: UserService) {}
}
