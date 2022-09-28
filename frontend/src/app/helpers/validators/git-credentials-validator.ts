/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidator,
  ValidationErrors,
} from '@angular/forms';
import { Observable, of } from 'rxjs';
import { GitService } from '../../services/git/git.service';

@Injectable({
  providedIn: 'root',
})
export class GitCredentialsValidator implements AsyncValidator {
  constructor(private gitService: GitService) {}

  validate(control: AbstractControl): Observable<ValidationErrors | null> {
    let credentials = {
      url: control.get('url')?.value,
      username: control.get('username')?.value,
      password: control.get('password')?.value,
    };
    return new Observable<ValidationErrors | null>((subscriber) => {
      this.gitService.fetch(credentials).subscribe({
        next: () => subscriber.next(null),
        error: (e) => subscriber.next({ credentials: { value: e.name } }),
      });
    });
  }
}
