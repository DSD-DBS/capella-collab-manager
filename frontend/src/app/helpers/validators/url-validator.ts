/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function absoluteUrlValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value: string = control.value;
    if (!value) return null;

    if (!hasAbsoluteUrlPrefix(value)) {
      return { urlSchemeError: 'Absolute URL must start with http(s)://' };
    }
    return null;
  };
}

export function absoluteOrRelativeValidators(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value: string = control.value;
    if (!value) return null;

    if (!(hasAbsoluteUrlPrefix(value) || hasRelativePathPrefix(value))) {
      return { urlSchemeError: 'URL must either start with http(s):// or /' };
    }
    return null;
  };
}

export function hasAbsoluteUrlPrefix(url: string): boolean {
  return url.startsWith('http://') || url.startsWith('https://');
}

export function hasRelativePathPrefix(path: string): boolean {
  return path.startsWith('/');
}
