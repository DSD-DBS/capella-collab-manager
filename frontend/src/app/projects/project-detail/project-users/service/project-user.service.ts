// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from 'src/app/services/auth/auth.service';

@Injectable({
  providedIn: 'root',
})
export class ProjectUserService {
  constructor(private http: HttpClient, private authService: AuthService) {}
}

export interface ProjectUser {
  permissions: Array<'read' | 'write'>;
  role: 'user' | 'manager' | 'administrator';
}
