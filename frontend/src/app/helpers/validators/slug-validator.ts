/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  AbstractControl,
  AsyncValidatorFn,
  ValidationErrors,
} from '@angular/forms';
import { map, Observable, take } from 'rxjs';
import slugify from 'slugify';
import { Project } from 'src/app/projects/service/project.service';

export function asyncProjectSlugValidator(
  projectObservable: Observable<Project[] | undefined>
): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> => {
    const projectSlug = slugify(control.value, { lower: true });
    return projectObservable.pipe(
      take(1),
      map((projects) => {
        return projects?.find((project) => project.slug === projectSlug)
          ? { uniqueSlug: { value: projectSlug } }
          : null;
      })
    );
  };
}
