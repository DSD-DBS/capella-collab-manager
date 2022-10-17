/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  EventEmitter,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  ValidationErrors,
  ValidatorFn,
  AbstractControl,
} from '@angular/forms';
import { Subscription } from 'rxjs';
import {
  absoluteOrRelativeSafetyValidators,
  absoluteUrlSafetyValidator,
  checkUrlForInvalidSequences,
  hasAbsoluteUrlPrefix,
  hasRelativePathPrefix,
} from 'src/app/helpers/validators/url-validator';
import {
  Credentials,
  GitService,
  Revisions,
} from 'src/app/services/git/git.service';
import { ModelService } from 'src/app/services/model/model.service';
import {
  CreateGitModel,
  GetGitModel,
  PatchGitModel,
  SourceService,
} from 'src/app/services/source/source.service';
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
import { cappellaSuffixValidator } from 'src/app/helpers/validators/validators';
import { Subscription } from 'rxjs';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { GitModelService } from '../../project-detail/model-overview/model-detail/git-model.service';

@Component({
  selector: 'app-create-coworking-method',
  templateUrl: './create-coworking-method.component.html',
  styleUrls: ['./create-coworking-method.component.css'],
})
export class CreateCoworkingMethodComponent implements OnInit, OnDestroy {
  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<{ created: boolean }>();

  public availableGitInstances: Array<GitSetting> = [];
  public selectedGitInstance: GitSetting | undefined = undefined;

  private availableRevisions: Revisions | undefined = {
    branches: [],
    tags: [],
  };
  public filteredRevisions: Revisions = { branches: [], tags: [] };

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
      this.existingRevisionValidator(),
    ]),
    entrypoint: new FormControl({ value: '/', disabled: true }),
    primary: new FormControl(),
  });

  private gitModelId: number | undefined;
  public gitModel: GetGitModel | undefined;

  public isEditMode: boolean = false;
  public editing: boolean = false;

  private gitSettingsSubscription?: Subscription;
  private modelSubscription?: Subscription;
  private revisionsSubscription?: Subscription;
  private gitModelSubscription?: Subscription;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitSettingsService: GitSettingsService,
    private gitService: GitService,
    private gitModelService: GitModelService,
    private sourceService: SourceService,
    private location: Location,
    private route: ActivatedRoute
  ) {}

  get urls() {
    return this.form.controls.urls.controls;
  }

  ngOnInit(): void {
    this.revisionsSubscription = this.gitService.revisions.subscribe(
      (revisions) => {
        this.availableRevisions = revisions;
        this.form.controls.revision.updateValueAndValidity();
      }
    );

    this.form.controls.revision.valueChanges.subscribe((value) =>
      this.filteredRevisionsByPrefix(value as string)
    );

    this.gitSettingsSubscription =
      this.gitSettingsService.gitSettings.subscribe((gitSettings) => {
        this.availableGitInstances = gitSettings;

        if (gitSettings.length) {
          this.urls.baseUrl.setValidators([Validators.required]);
          this.urls.inputUrl.setValidators([
            absoluteOrRelativeSafetyValidators(),
          ]);
        }
        this.form.controls.urls.setValidators([this.resultUrlValidator()]);

        if (this.isEditMode) {
          this.fillFormWithGitModel(this.gitModel!);
          this.gitService.loadRevisions(
            this.resultUrl,
            this.form.value.credentials as Credentials
          );
        }
      });

    this.modelSubscription = this.modelService._model.subscribe((model) => {
      if (model?.tool.name === 'Capella') {
        this.form.controls.entrypoint.addValidators(cappellaSuffixValidator());
      }
    });

    this.gitModelId = this.route.snapshot.params['git-model'];
    this.isEditMode = !!this.gitModelId;

    if (this.isEditMode) {
      this.form.disable();

      this.gitModelSubscription = this.gitModelService.gitModel.subscribe(
        (gitModel) => (this.gitModel = gitModel)
      );

      this.gitModelService.loadGitModelById(
        this.projectService.project!.slug,
        this.modelService.model!.slug,
        this.gitModelId!
      );
    }

    this.gitSettingsService.loadGitSettings();
  }

  ngOnDestroy(): void {
    this.gitSettingsSubscription?.unsubscribe();
    this.modelSubscription?.unsubscribe();
    this.revisionsSubscription?.unsubscribe();
    this.gitModelSubscription?.unsubscribe();
  }

  onRevisionFocus(): void {
    if (this.form.controls.urls.valid) {
      this.gitService.loadRevisions(
        this.resultUrl,
        this.form.value.credentials as Credentials
      );
    }
  }

  onSelect(value: GitSetting): void {
    let inputUrlControl = this.urls.inputUrl;
    let inputUrl = inputUrlControl.value;

    if (inputUrl && !hasRelativePathPrefix(inputUrl)) {
      inputUrlControl.reset();
    }

    this.selectedGitInstance = value;
    this.updateResultUrl();
    this.resetRevisions();
  }

  onInputChange(changedInputUrl: string): void {
    this.updateResultUrl();
    this.resetRevisions();

    this.urls.inputUrl.updateValueAndValidity();

    if (changedInputUrl && hasAbsoluteUrlPrefix(changedInputUrl)) {
      let longestMatchingGitSetting =
        this.findLongestUrlMatchingGitSetting(changedInputUrl);
      if (longestMatchingGitSetting) {
        this.selectedGitInstance = longestMatchingGitSetting;
        this.urls.baseUrl.setValue(longestMatchingGitSetting);
      } else if (this.availableGitInstances.length) {
        this.selectedGitInstance = undefined;
        this.urls.baseUrl.reset();
      }
    }
  }

  onCreateSubmit(): void {
    if (this.form.valid) {
      this.sourceService
        .addGitSource(
          this.projectService.project?.slug!,
          this.modelService.model?.slug!,
          this.createGitModelFromForm()
        )
        .subscribe(() => {
          if (this.asStepper) {
            this.create.emit({ created: true });
          } else {
            this.location.back();
          }
        });
    }
  }

  onEditSubmit(): void {
    if (this.form.valid) {
      const patchGitModel = this.createGitModelFromForm() as PatchGitModel;
      patchGitModel.primary = this.form.value.primary;

      this.gitModelService
        .updateGitInstance(
          this.projectService.project?.slug!,
          this.modelService.model?.slug!,
          this.gitModelId!,
          patchGitModel
        )
        .subscribe(() => this.location.back());
    }
  }

  enableEditing(): void {
    this.editing = true;
    this.form.enable();
    if (this.gitModel!.primary) {
      this.form.controls.primary.disable();
    }
    this.form.controls.credentials.controls.password.setValue('');
    this.form.updateValueAndValidity();
  }

  cancelEditing(): void {
    this.editing = false;
    this.form.disable();
    this.fillFormWithGitModel(this.gitModel!);
  }

  private createGitModelFromForm(): CreateGitModel {
    return {
      path: this.resultUrl,
      revision: this.form.value.revision!,
      entrypoint: this.form.value.entrypoint!,
      username: this.form.value.credentials?.username!,
      password: this.form.value.credentials?.password!,
    };
  }

  private fillFormWithGitModel(gitModel: GetGitModel): void {
    let credentials = this.form.controls.credentials.controls;

    this.urls.inputUrl.setValue(gitModel.path);

    if (this.gitModel?.username) {
      credentials.username.setValue(gitModel?.username!);
    }

    if (this.gitModel?.password) {
      credentials.password.setValue('placeholder');
    }

    this.form.controls.revision.setValue(gitModel.revision);
    this.form.controls.entrypoint.setValue(gitModel.entrypoint);
    this.form.controls.primary.setValue(this.gitModel?.primary);
  }

  private updateResultUrl(): void {
    let baseUrl = this.selectedGitInstance?.url || '';
    let inputUrl = this.urls.inputUrl.value!;

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
    this.form.controls.primary.disable();
    this.form.controls.credentials.disable();
    this.form.controls.entrypoint.disable();
    this.form.controls.revision.disable();
  }

  private enableAllExceptUrls() {
    if (this.isEditMode && !this.gitModel!.primary) {
      this.form.controls.primary.enable();
    }
    this.form.controls.credentials.enable();
    this.form.controls.entrypoint.enable();
    this.form.controls.revision.enable();
  }

  private resultUrlValidator(): ValidatorFn {
    return (_: AbstractControl): ValidationErrors | null => {
      this.updateResultUrl();

      let baseUrl = this.urls.baseUrl;
      let inputUrl = this.urls.inputUrl;

      let innerValidationResult: ValidationErrors | null = null;
      let url: string = this.resultUrl;
      if (!url) return { required: 'Resulting URL is required' };

      if (!hasAbsoluteUrlPrefix(url)) {
        innerValidationResult = {
          urlPrefixError: 'Absolute URL must start with http(s)://',
        };
      } else if (this.availableGitInstances && baseUrl.invalid) {
        innerValidationResult = baseUrl.errors;
      } else if (inputUrl.invalid) {
        innerValidationResult = inputUrl.errors;
      }

      const outerValidationResult = checkUrlForInvalidSequences(url);

      if (!innerValidationResult && !outerValidationResult) {
        this.enableAllExceptUrls();
      } else {
        this.disableAllExpectUrls();
        return Object.assign({}, outerValidationResult, innerValidationResult);
      }
      return null;
    };
  }

  private existingRevisionValidator(): ValidatorFn {
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
