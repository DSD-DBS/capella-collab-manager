/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

const urlBlacklistSequences: string[] = ['..', '%'];

export function absoluteUrlSafetyValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    let value: string = control.value;
    if (!value) return null;

    if (!hasAbsoluteUrlPrefix(value)) {
      return { urlPrefixError: 'Absolute URL must start with http(s)://' };
    }
    return checkUrlForInvalidSequences(value);
  };
}

export function relativeUrlSafetyValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    let value: string = control.value;
    if (!value) return null;

    if (!hasRelativePathPrefix(value)) {
      return { urlPrefixErrors: 'Relative URL must start with /' };
    }
    return checkUrlForInvalidSequences(value);
  };
}

export function absoluteOrRelativeSafetyValidators(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    let value: string = control.value;
    if (!value) return null;

    if (!(hasAbsoluteUrlPrefix(value) || hasRelativePathPrefix(value))) {
      return { urlPrefixError: 'URL must either start with http(s):// or /' };
    }
    return checkUrlForInvalidSequences(value);
  };
}

export function checkUrlForInvalidSequences(url: string) {
  let foundSeq: string[] = [];
  urlBlacklistSequences.forEach((seq) => {
    if (url.includes(seq)) {
      foundSeq.push(seq);
    }
  });

  if (foundSeq.length) {
    return {
      urlSafetyError: `URL contains the following invalid sequences: ${foundSeq.join(
        ', '
      )}`,
    };
  }
  return null;
}

export function hasAbsoluteUrlPrefix(url: string): boolean {
  return url.startsWith('http://') || url.startsWith('https://');
}

export function hasRelativePathPrefix(path: string): boolean {
  return path.startsWith('/');
}
