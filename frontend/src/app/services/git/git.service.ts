/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Injectable, inject } from '@angular/core';
import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
  ValidatorFn,
} from '@angular/forms';
import { BehaviorSubject, map, Observable, take } from 'rxjs';
import {
  GetRevisionsResponseModel,
  GitCredentials,
  ProjectsModelsGitService,
  SettingsModelsourcesGitService,
} from 'src/app/openapi';

@Injectable({
  providedIn: 'root',
})
export class GitService {
  private gitSettingsService = inject(SettingsModelsourcesGitService);
  private gitModelService = inject(ProjectsModelsGitService);

  private _revisions = new BehaviorSubject<
    GetRevisionsResponseModel | undefined
  >(undefined);

  public readonly revisions$ = this._revisions.asObservable();

  loadRevisions(gitUrl: string, credentials: GitCredentials): void {
    this.gitSettingsService
      .getRevisions({
        credentials: credentials,
        url: gitUrl,
      })
      .subscribe({
        next: (revisions) => this._revisions.next(revisions),
        error: () => this._revisions.next(undefined),
      });
  }

  loadPrivateRevisions(
    gitUrl: string,
    projectSlug: string,
    modelSlug: string,
    gitModelId: number,
  ): void {
    this.gitModelService
      .getRevisionsWithModelCredentials(
        projectSlug,
        gitModelId,
        modelSlug,
        gitUrl,
      )
      .subscribe({
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

export function existingRevisionValidator(
  revisions: GetRevisionsResponseModel,
): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const revision = control.value;

    const isInBranches = revisions.branches.includes(revision);
    const isInTags = revisions.tags.includes(revision);

    return !(isInBranches || isInTags)
      ? { revisionNotFoundError: `${revision} does not exist` }
      : null;
  };
}
