/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  ValidationErrors,
  ValidatorFn,
  AbstractControl,
} from '@angular/forms';
import { ProjectService } from 'src/app/services/project/project.service';
import {
  Credentials,
  GitService,
  Instance,
} from 'src/app/services/git/git.service';
import { ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { Source, SourceService } from 'src/app/services/source/source.service';
import {
  GitSetting,
  GitSettingsService,
} from 'src/app/services/settings/git-settings.service';
import {
  absoluteOrRelativeSafetyValidators,
  absoluteUrlSafetyValidator,
  checkUrlForInvalidSequences,
  hasAbsoluteUrlPrefix,
  hasRelativePathPrefix,
} from 'src/app/helpers/validators/url-validator';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css'],
})
export class CreateCoworkingMethodComponent implements OnInit {
  @Output() create = new EventEmitter<{ created: boolean }>();

  public availableGitInstances: Array<GitSetting> = [];
  public selectedGitInstance: GitSetting | undefined = undefined;

  private availableRevisions: Instance | undefined = {
    branches: [],
    tags: [],
  };
  public filteredRevisions: Instance = { branches: [], tags: [] };

  public resultUrl: string = '';

  public form = new FormGroup({
    urls: new FormGroup({
      baseUrl: new FormControl<GitSetting | undefined>(undefined),
      inputUrl: new FormControl('', absoluteUrlSafetyValidator()),
    }),
    credentials: new FormGroup({
      username: new FormControl({ value: '', disabled: true }),
      password: new FormControl({ value: '', disabled: true }),
    }),
    revision: new FormControl({ value: '', disabled: true }, [
      Validators.required,
      this.validRevisionValidator(),
    ]),
    entrypoint: new FormControl({ value: '/', disabled: true }),
  });

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public gitSettingsService: GitSettingsService,
    private gitService: GitService,
    private sourceService: SourceService
  ) {}

  ngOnInit(): void {
    this.gitService.instance.subscribe((revisions) => {
      this.availableRevisions = revisions;
      this.form.controls.revision.updateValueAndValidity({
        onlySelf: false,
        emitEvent: true,
      });
    });

    this.gitSettingsService.gitSettings.subscribe((gitSettings) => {
      this.availableGitInstances = gitSettings;

      if (gitSettings.length) {
        this.form.controls.urls.controls.baseUrl.setValidators([
          Validators.required,
        ]);
        this.form.controls.urls.controls.inputUrl.setValidators([
          absoluteOrRelativeSafetyValidators(),
        ]);
      }
      this.form.controls.urls.setValidators([this.resultUrlValidator()]);
    });

    this.form.controls.revision.valueChanges.subscribe((value) =>
      this.filteredRevisionsByPrefix(value as string)
    );

    this.gitSettingsService.loadGitSettings();
  }

  onRevisionFocus(): void {
    let urls = this.form.controls.urls;
    if (
      urls.invalid ||
      urls.controls.baseUrl.invalid ||
      urls.controls.inputUrl.invalid
    ) {
      return;
    }

    let gitCredentials = this.form.controls.credentials.value as Credentials;

    this.gitService.loadInstance(this.resultUrl, gitCredentials);
  }

  onSelect(value: GitSetting): void {
    let inputUrlFormControl = this.form.controls.urls.controls.inputUrl;
    let inputUrl = inputUrlFormControl.value;

    if (inputUrl && !hasRelativePathPrefix(inputUrl)) {
      inputUrlFormControl.reset();
    }

    this.selectedGitInstance = value;
    this.updateResultUrl();
    this.resetRevisions();
  }

  onInputChange(changedInputUrl: string): void {
    this.updateResultUrl();
    this.resetRevisions();

    let urlsControls = this.form.controls.urls.controls;
    urlsControls.inputUrl.updateValueAndValidity();

    if (changedInputUrl && hasAbsoluteUrlPrefix(changedInputUrl)) {
      let longestMatchingGitSetting =
        this.findLongestUrlMatchingGitSetting(changedInputUrl);

      if (longestMatchingGitSetting) {
        urlsControls.baseUrl.setValue(longestMatchingGitSetting);
        this.selectedGitInstance = longestMatchingGitSetting;
      } else if (this.availableGitInstances.length) {
        this.selectedGitInstance = undefined;
        this.form.controls.urls.controls.baseUrl.reset();
      }
    }
  }

  onSubmit(): void {
    if (
      this.form.valid &&
      this.projectService.project &&
      this.modelService.model
    ) {
      this.sourceService
        .addGitSource(
          this.projectService.project.name,
          this.modelService.model.slug,
          {
            path: this.resultUrl,
            username: this.form.value.credentials!.username || '',
            password: this.form.value.credentials!.password || '',
            revision: this.form.value.revision!,
            entrypoint: this.form.value.entrypoint || '',
          } as Source
        )
        .subscribe(() => {
          this.create.emit({ created: true });
        });
    }
  }

  private updateResultUrl(): void {
    let inputUrlFormControl = this.form.controls.urls.controls.inputUrl;

    let baseUrl = this.selectedGitInstance?.url || '';
    let inputUrl = inputUrlFormControl.value || '';

    if (hasAbsoluteUrlPrefix(inputUrl)) {
      this.resultUrl = inputUrl;
    } else {
      this.resultUrl = baseUrl + inputUrl;
    }
  }

  private filteredRevisionsByPrefix(prefix: string): void {
    this.filteredRevisions = {
      branches: [],
      tags: [],
    };

    if (this.availableRevisions) {
      this.filteredRevisions = {
        branches: this.availableRevisions!.branches.filter((branch) =>
          branch.startsWith(prefix)
        ),
        tags: this.availableRevisions!.tags.filter((tag) =>
          tag.startsWith(prefix)
        ),
      };
    }
  }

  private resetRevisions() {
    this.availableRevisions = undefined;
    this.filteredRevisions = {
      branches: [],
      tags: [],
    };
    this.form.controls.revision.setValue('');
  }

  private disableAllExpectUrls() {
    this.form.controls.credentials.disable();
    this.form.controls.entrypoint.disable();
    this.form.controls.revision.disable();
  }

  private enableAllExceptUrls() {
    this.form.controls.credentials.enable();
    this.form.controls.entrypoint.enable();
    this.form.controls.revision.enable();
  }

  private resultUrlValidator(): ValidatorFn {
    return (_: AbstractControl): ValidationErrors | null => {
      this.updateResultUrl();

      let baseUrl = this.form.controls.urls.controls.baseUrl;
      let inputUrl = this.form.controls.urls.controls.inputUrl;

      let url: string = this.resultUrl;
      if (!url) return { required: 'Resulting URL is required' };

      if (!hasAbsoluteUrlPrefix(url)) {
        return { urlPrefixError: 'Absolute URL must start with http(s)://' };
      } else if (this.availableGitInstances && baseUrl.invalid) {
        return baseUrl.errors;
      } else if (inputUrl.invalid) {
        return inputUrl.errors;
      }

      let validationResult = checkUrlForInvalidSequences(url);

      if (!validationResult) {
        this.enableAllExceptUrls();
      } else {
        this.disableAllExpectUrls();
      }
      return validationResult;
    };
  }

  private validRevisionValidator(): ValidatorFn {
    return (controls: AbstractControl): ValidationErrors | null => {
      let value: string = controls.value;
      if (!value) return null;

      if (
        this.availableRevisions?.branches.includes(value) ||
        this.availableRevisions?.tags.includes(value)
      ) {
        return null;
      }

      return {
        revisionNotFoundError: `${value} does not exist on ${this.resultUrl}`,
      };
    };
  }

  private findLongestUrlMatchingGitSetting(
    url: string
  ): GitSetting | undefined {
    let longestMatchingGitSetting = undefined;
    let longestUrlLength = 0;
    this.availableGitInstances.forEach((gitSetting) => {
      if (
        url.startsWith(gitSetting.url) &&
        gitSetting.url.length > longestUrlLength
      ) {
        longestMatchingGitSetting = gitSetting;
        longestUrlLength = gitSetting.url.length;
      }
    });

    return longestMatchingGitSetting;
  }
}
