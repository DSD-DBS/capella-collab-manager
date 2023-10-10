/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function lowerCaseValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    if (control.value != control.value.toLowerCase() && control.value) {
      return { lowerCaseError: true };
    }
    return null;
  };
}

export function regExpValidator(
  ruleRegExp: RegExp,
  value: string,
  errors: ValidationErrors,
): ValidationErrors | null {
  if (!ruleRegExp.test(value)) {
    return errors;
  }
  return null;
}
