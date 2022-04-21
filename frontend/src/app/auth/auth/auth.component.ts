// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import {
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges,
} from '@angular/core';
import { AuthService } from 'src/app/services/auth/auth.service';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css'],
})
export class AuthComponent implements OnInit {
  @Input()
  set autoLogin(value: boolean) {
    if (value) {
      this.webSSO();
    }
  }

  constructor(private authService: AuthService) {}

  ngOnInit(): void {}

  webSSO() {
    this.authService.getRedirectURL().subscribe((res) => {
      window.location.href = res.auth_url;
    });
  }
}
