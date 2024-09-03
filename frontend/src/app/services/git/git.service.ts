/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import { BehaviorSubject, map, Observable, take } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface Credentials {
  username: string;
  password: string;
}

export interface Revisions {
  branches: string[];
  tags: string[];
}

@Injectable({
  providedIn: 'root',
})
export class GitService {
  BACKEND_URL_PREFIX = environment.backend_url;

  private _revisions = new BehaviorSubject<Revisions | undefined>(undefined);

  public readonly revisions$ = this._revisions.asObservable();

  constructor(private http: HttpClient) {}

  loadRevisions(gitUrl: string, credentials: Credentials): void {
    this.http
      .post<Revisions>(
        this.BACKEND_URL_PREFIX + '/settings/modelsources/git/revisions',
        {
          credentials: credentials,
          url: gitUrl,
        },
      )
      .subscribe({
        next: (revisions) => this._revisions.next(revisions),
        error: () => this._revisions.next(undefined),
      });
  }

  getPrivateRevision(
    gitUrl: string,
    projectSlug: string,
    modelSlug: string,
    gitModelId: number,
  ): Observable<Revisions> {
    return this.http.post<Revisions>(
      this.BACKEND_URL_PREFIX +
        `/projects/${projectSlug}/models/${modelSlug}/modelsources/git/${gitModelId}/revisions`,
      gitUrl,
    );
  }

  loadPrivateRevisions(
    gitUrl: string,
    projectSlug: string,
    modelSlug: string,
    gitModelId: number,
  ): void {
    this.getPrivateRevision(
      gitUrl,
      projectSlug,
      modelSlug,
      gitModelId,
    ).subscribe({
      next: (revisions) => this._revisions.next(revisions),
      error: () => this._revisions.next(undefined),
    });
  }

  clearRevision(): void {
    this._revisions.next(undefined);
  }

  asyncExistingRevisionValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return this.revisions$.pipe(
        take(1),
        map((revisions) => {
          const revision = control.value;
          return revisions?.branches.includes(revision) ||
            revisions?.tags.includes(revision)
            ? null
            : { revisionNotFoundError: `${revision} does not exist` };
        }),
      );
    };
  }
}

export function existingRevisionValidator(revisions: Revisions): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const revision = control.value;

    const isInBranches = revisions.branches.includes(revision);
    const isInTags = revisions.tags.includes(revision);

    return !(isInBranches || isInTags)
      ? { revisionNotFoundError: `${revision} does not exist` }
      : null;
  };
}
