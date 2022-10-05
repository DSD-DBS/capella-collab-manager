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
import { Source, SourceService } from 'src/app/services/source/source.service';
import {
  GitSetting,
  GitSettingsService,
} from 'src/app/services/settings/git-settings.service';
import {
  absoluteOrRelativeUrlPrefixValidator,
  checkUrlForInvalidSequences,
} from 'src/app/helpers/validators/url-validator';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css'],
})
export class CreateCoworkingMethodComponent implements OnInit {
  @Output() create = new EventEmitter<{ created: boolean }>();

  public cmpGitSettings: Array<GitSetting> = [];
  public filteredRevisions: Instance = { branches: [], tags: [] };
  public selectedGitSetting: GitSetting | undefined = undefined;

  public resultUrl: string = '';

  private instances: Instance | undefined = {
    branches: [],
    tags: [],
  };

  public form = new FormGroup({
    urlGroup: new FormGroup({
      baseUrl: new FormControl<GitSetting | undefined>(undefined),
      inputUrl: new FormControl('', absoluteOrRelativeUrlPrefixValidator()),
    }),
    credentials: new FormGroup({
      username: new FormControl(''),
      password: new FormControl(''),
    }),
    revision: new FormControl('', Validators.required),
    entrypoint: new FormControl('/'),
  });

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public gitSettingsService: GitSettingsService,
    private gitService: GitService,
    private sourceService: SourceService
  ) {}

  ngOnInit(): void {
    this.gitService.instance.subscribe({
      next: (instance) => {
        this.instances = instance;
        this.form.controls.revision.updateValueAndValidity({
          onlySelf: false,
          emitEvent: true,
        });
      },
    });

    this.form.controls.revision.valueChanges.subscribe((value) =>
      this.filteredRevisionsByPrefix(value as string)
    );

    this.gitSettingsService.gitSettings.subscribe({
      next: (gitSettings) => {
        this.cmpGitSettings = gitSettings;
      },
    });
    this.gitSettingsService.loadGitSettings();

    this.form.controls.urlGroup.setValidators(this.urlValidation());
    this.initializeBaseUrlValidator();
  }

  onRevisionFocus(): void {
    let projectName = this.projectService?.project?.name || '';
    let url = this.resultUrl;
    let gitCredentials = this.form.controls.credentials.value as Credentials;

    if (url) {
      this.gitService.loadInstance(projectName, url, gitCredentials);
    }
  }

  onSelect(value: GitSetting): void {
    let inputUrlFormControl = this.form.controls.urlGroup.controls.inputUrl;
    let inputUrl = inputUrlFormControl.value;

    if (inputUrl && !inputUrl.startsWith('/')) {
      inputUrlFormControl.reset();
    }

    this.selectedGitSetting = value;
    this.updateResultUrl();
  }

  onInputChange(changedInputUrl: string): void {
    this.updateResultUrl();
    this.form.controls.urlGroup.controls.inputUrl.updateValueAndValidity();

    if (changedInputUrl && changedInputUrl.startsWith('http')) {
      let longestMatchingGitSetting =
        this.findLongestUrlMatchingGitSetting(changedInputUrl);

      if (longestMatchingGitSetting) {
        this.form.controls.urlGroup.controls.baseUrl.setValue(
          longestMatchingGitSetting
        );
        this.selectedGitSetting = longestMatchingGitSetting;
      } else if (this.cmpGitSettings.length) {
        this.resetResultAndBaseUrl();
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
          this.createSourceFromForm()
        )
        .subscribe(() => {
          this.create.emit({ created: true });
        });
    }
  }

  private updateResultUrl(): void {
    let inputUrlFormControl = this.form.controls.urlGroup.controls.inputUrl;

    let baseUrl = this.selectedGitSetting?.url || '';
    let inputUrl = inputUrlFormControl.value;

    if (
      inputUrl?.startsWith('http') &&
      this.selectedGitSetting &&
      inputUrl.startsWith(this.selectedGitSetting.url)
    ) {
      this.resultUrl = inputUrl;
    } else {
      this.resultUrl = baseUrl + (inputUrl || inputUrlFormControl.value || '');
    }
  }

  private resetResultAndBaseUrl() {
    this.resultUrl = '';
    this.selectedGitSetting = undefined;
    this.form.controls.urlGroup.controls.baseUrl.reset();
  }

  private filteredRevisionsByPrefix(prefix: string): void {
    this.filteredRevisions = {
      branches: [],
      tags: [],
    };

    if (this.instances) {
      this.filteredRevisions = {
        branches: this.instances!.branches.filter((branch) =>
          branch.startsWith(prefix)
        ),
        tags: this.instances!.tags.filter((tag) => tag.startsWith(prefix)),
      };
    }
  }

  private findLongestUrlMatchingGitSetting(
    url: string
  ): GitSetting | undefined {
    let longestMatchingGitSetting = undefined;
    let longestUrlLength = 0;
    this.cmpGitSettings.forEach((gitSetting) => {
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

  private createSourceFromForm(): Source {
    return {
      path: this.resultUrl,
      username: this.form.value.credentials!.username || '',
      password: this.form.value.credentials!.password || '',
      revision: this.form.value.revision!,
      entrypoint: this.form.value.entrypoint || '',
    };
  }

  private initializeBaseUrlValidator(): void {
    let baseUrlFormGroup = this.form.controls.urlGroup.controls.baseUrl;

    if (this.cmpGitSettings.length) {
      baseUrlFormGroup.setValidators([Validators.required]);
    }
    baseUrlFormGroup.updateValueAndValidity();
  }

  private urlValidation(): ValidatorFn {
    return (_: AbstractControl): ValidationErrors | null => {
      this.updateResultUrl();

      let url: string = this.resultUrl;
      if (!url) return null;

      if (!(url.startsWith('http://') || url.startsWith('https://'))) {
        return { urlPrefixError: 'Absolute URL must start with http(s)://' };
      }
      return checkUrlForInvalidSequences(url);
    };
  }
}
