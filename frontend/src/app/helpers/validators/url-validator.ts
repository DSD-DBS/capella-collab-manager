/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

const urlBlacklistSequences: string[] = ['..', '%'];

export function absoluteUrlSafetyValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    let url: string = control.value;
    if (!url) return null;

    if (!(url.startsWith('http://') || url.startsWith('https://'))) {
      return { urlPrefixError: 'Absolute URL must start with http(s)://' };
    }
    return checkUrlForInvalidSequences(url);
  };
}

export function relativeUrlSafetyValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    let url: string = control.value;
    if (!url) return null;

    if (!url.startsWith('/')) {
      return { urlPrefixErrors: 'Relative URL must start with /' };
    }
    return checkUrlForInvalidSequences(url);
  };
}

export function absoluteOrRelativeSafetyValidators(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    let url: string = control.value;
    if (!url) return null;

    if (
      !(url.startsWith('http://') || url.startsWith('https://')) &&
      !url.startsWith('/')
    ) {
      return { urlPrefixError: 'URL must either start with http(s):// or /' };
    }
    return checkUrlForInvalidSequences(url);
  };
}

export function absoluteOrRelativeUrlPrefixValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    let value = control.value;
    if (value && !value.startsWith('http') && !value.startsWith('/')) {
      return { urlPrefixError: 'URL must either start with "http" or "/"' };
    }
    return null;
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
