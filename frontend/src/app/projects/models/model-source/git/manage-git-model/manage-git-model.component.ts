/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  ValidationErrors,
  ValidatorFn,
  AbstractControl,
  AsyncValidatorFn,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map, Observable, of } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  absoluteOrRelativeValidators,
  absoluteUrlValidator,
  hasAbsoluteUrlPrefix,
  hasRelativePathPrefix,
} from 'src/app/helpers/validators/url-validator';
import { ModelService } from 'src/app/projects/models/service/model.service';
import {
  CreateGitModel,
  GetGitModel,
  GitModelService,
  PatchGitModel,
} from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import {
  Credentials,
  GitService,
  Revisions,
} from 'src/app/services/git/git.service';
import {
  GitInstance,
  GitInstancesService,
} from 'src/app/settings/modelsources/git-settings/service/git-instances.service';

@UntilDestroy()
@Component({
  selector: 'app-manage-git-model',
  templateUrl: './manage-git-model.component.html',
  styleUrls: ['./manage-git-model.component.css'],
})
export class ManageGitModelComponent implements OnInit {
  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<boolean>();

  public availableGitInstances: Array<GitInstance> | undefined = undefined;
  public selectedGitInstance: GitInstance | undefined = undefined;

  private availableRevisions: Revisions | undefined = {
    branches: [],
    tags: [],
  };
  public filteredRevisions: Revisions = { branches: [], tags: [] };

  public resultUrl: string = '';

  public form = new FormGroup({
    urls: new FormGroup({
      baseUrl: new FormControl<GitInstance | undefined>(undefined),
      inputUrl: new FormControl('', absoluteUrlValidator()),
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

  private projectSlug?: string = undefined;
  private modelSlug?: string = undefined;

  private gitModelId?: number;
  public gitModel?: GetGitModel;

  public isEditMode: boolean = false;
  public editing: boolean = false;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitSettingsService: GitInstancesService,
    private gitService: GitService,
    private gitModelService: GitModelService,
    private toastService: ToastService,
    private breadCrumbsService: BreadcrumbsService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  get urls() {
    return this.form.controls.urls.controls;
  }

  ngOnInit(): void {
    this.gitService.revisions
      .pipe(untilDestroyed(this))
      .subscribe((revisions) => {
        this.availableRevisions = revisions;
        this.form.controls.revision.updateValueAndValidity();
      });

    this.form.controls.revision.valueChanges.subscribe((value) =>
      this.filteredRevisionsByPrefix(value as string)
    );
    this.gitSettingsService.gitSettings
      .pipe(untilDestroyed(this))
      .subscribe((gitSettings) => {
        this.availableGitInstances = gitSettings;

  <<<<<<< HEAD
      this.gitSettingsService.gitInstances.subscribe((gitSettings) => {
        this.availableGitInstances = gitSettings;

        if (gitSettings?.length) {
          this.urls.baseUrl.setValidators([Validators.required]);
          this.urls.inputUrl.setValidators([absoluteOrRelativeValidators()]);
          this.form.controls.urls.setAsyncValidators([
            this.resultUrlPrefixAsyncValidator(),
          ]);
        } else {
          this.urls.inputUrl.addValidators([Validators.required]);
        }
      });
      if (gitSettings.length) {
        this.urls.baseUrl.setValidators([Validators.required]);
        this.urls.inputUrl.setValidators([absoluteOrRelativeValidators()]);
        this.form.controls.urls.setAsyncValidators([
          this.resultUrlPrefixAsyncValidator(),
        ]);
      } else {
        this.urls.inputUrl.addValidators([Validators.required]);
      }
    });

    this.modelService.model.subscribe((model) => {
=======
      if (gitSettings.length) {
          this.urls.baseUrl.setValidators([Validators.required]);
          this.urls.inputUrl.setValidators([absoluteOrRelativeValidators()]);
          this.form.controls.urls.setAsyncValidators([
            this.resultUrlPrefixAsyncValidator(),
          ]);
        } else {
          this.urls.inputUrl.addValidators([Validators.required]);
        }
      });

    this.modelService.model.pipe(untilDestroyed(this)).subscribe((model) => {
      this.modelSlug = model?.slug!;
>>>>>>> b2ae2aac (feat: Apply new fetching approach to projects)
      if (model?.tool.name === 'Capella') {
        this.form.controls.entrypoint.addValidators(
          Validators.pattern(/^$|\.aird$/)
        );
      }
    });

    this.projectService.project
      .pipe(untilDestroyed(this))
      .subscribe((project) => {
        this.projectSlug = project?.slug;

        this.route.params
          .pipe(
            filter((params) => !!params['git-model']),
            map((params) => params['git-model'])
          )
          .subscribe((gitModelId) => {
            this.isEditMode = true;
            this.gitModelId = gitModelId;
            this.form.disable();

            this.gitModelService.gitModel
              .pipe(untilDestroyed(this))
              .subscribe((gitModel) => {
                this.gitModel = gitModel;
                this.fillFormWithGitModel(gitModel!);

                this.breadCrumbsService.updatePlaceholder({ gitModel });

                this.gitService.loadPrivateRevisions(
                  gitModel!.path,
                  this.projectSlug!,
                  this.modelSlug!,
                  gitModelId
                );
              });

            this.gitModelService.loadGitModelById(
              this.projectSlug!,
              this.modelSlug!,
              gitModelId
            );
          });
      });

    this.gitSettingsService.loadGitInstances();
  }

  ngOnDestroy(): void {
    this.breadCrumbsService.updatePlaceholder({ gitModel: undefined });
  }

  onRevisionFocus(): void {
    if (this.form.controls.urls.valid) {
      if (
        this.isEditMode &&
        !this.form.controls.credentials.controls.password.value
      ) {
        this.gitService.loadPrivateRevisions(
          this.resultUrl,
          this.projectSlug!,
          this.modelSlug!,
          this.gitModelId!
        );
      } else {
        this.gitService.loadRevisions(
          this.resultUrl,
          this.form.value.credentials as Credentials
        );
      }
    }
  }

  onBaseIntegrationUrlSelect(value: GitInstance): void {
    let inputUrlControl = this.urls.inputUrl;
    let inputUrl = inputUrlControl.value;

    if (inputUrl && !hasRelativePathPrefix(inputUrl)) {
      inputUrlControl.reset();
    }

    this.selectedGitInstance = value;
    this.form.controls.urls.updateValueAndValidity();
    this.resetRevisions();
  }

  onUrlInputChange(changedInputUrl: string): void {
    this.updateResultUrl();
    this.resetRevisions();

    if (!this.availableGitInstances?.length) {
      if (this.form.controls.urls.controls.inputUrl.valid) {
        this.enableAllExceptUrls();
      } else {
        this.disableAllExpectUrls();
      }
    }

    this.urls.inputUrl.updateValueAndValidity();

    if (changedInputUrl && hasAbsoluteUrlPrefix(changedInputUrl)) {
      let longestMatchingGitSetting =
        this.findLongestUrlMatchingGitSetting(changedInputUrl);
      if (longestMatchingGitSetting) {
        this.selectedGitInstance = longestMatchingGitSetting;
        this.urls.baseUrl.setValue(longestMatchingGitSetting);
      } else if (this.availableGitInstances?.length) {
        this.selectedGitInstance = undefined;
        this.urls.baseUrl.reset();
        this.disableAllExpectUrls();
      }
    }
  }

  onCreateSubmit(): void {
    if (this.form.valid) {
      this.gitModelService
        .addGitSource(
          this.projectSlug!,
          this.modelSlug!,
          this.createGitModelFromForm()
        )
        .subscribe(() => {
          if (this.asStepper) {
            this.create.emit(true);
          } else {
            this.router.navigate(['../..'], { relativeTo: this.route });
          }
        });
    }
  }

  onEditSubmit(): void {
    if (this.form.valid) {
      const patchGitModel = this.createGitModelFromForm() as PatchGitModel;
      patchGitModel.primary = this.form.controls.primary.value;

      this.gitModelService
        .updateGitRepository(
          this.projectSlug!,
          this.modelSlug!,
          this.gitModelId!,
          patchGitModel
        )
        .subscribe(() =>
          this.router.navigate(['../..'], { relativeTo: this.route })
        );
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

  unlinkGitModel(): void {
    if (!window.confirm(`Do you really want to unlink this Git model?`)) {
      return;
    }

    this.gitModelService
      .deleteGitSource(this.projectSlug!, this.modelSlug!, this.gitModel!)
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'Git model deleted',
            `${this.gitModel!.path} has been deleted`
          );
          this.router.navigateByUrl(
            `/project/${this.projectSlug}/model/${this.modelSlug!}`
          );
        },
        error: () => {
          this.toastService.showError(
            'Git model deletion failed',
            `${this.gitModel!.path} has not been deleted`
          );
        },
      });
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
    this.urls.inputUrl.setValue(gitModel.path);

    const credentials = this.form.controls.credentials.controls;
    credentials.username.setValue(gitModel.username!);

    if (gitModel.password) {
      credentials.password.setValue('placeholder');
    }

    this.form.controls.revision.setValue(gitModel.revision);
    this.form.controls.entrypoint.setValue(gitModel.entrypoint);
    this.form.controls.primary.setValue(gitModel.primary);
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

  private resultUrlPrefixAsyncValidator(): AsyncValidatorFn {
    return (_: AbstractControl): Observable<ValidationErrors | null> => {
      this.updateResultUrl();

      if (!this.resultUrl) return of({ required: 'Resulting URL is required' });

      return this.gitModelService
        .validatePath(this.projectSlug!, this.modelSlug!, this.resultUrl)
        .pipe(
          map((prefixExists: boolean) => {
            if (prefixExists) {
              this.enableAllExceptUrls();
              return null;
            }

            this.disableAllExpectUrls();
            return {
              urlPrefixError:
                "The resolved URL doesn't match with one of the allowed git instances",
            };
          })
        );
    };
  }

  private updateResultUrl() {
    let baseUrl = this.selectedGitInstance?.url || '';
    let inputUrl = this.urls.inputUrl.value!;

    if (hasAbsoluteUrlPrefix(inputUrl)) {
      this.resultUrl = inputUrl;
    } else {
      this.resultUrl = baseUrl + inputUrl;
    }
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
  ): GitInstance | undefined {
    let longestMatchingGitSetting = undefined;
    let longestUrlLength = 0;
    this.availableGitInstances?.forEach((gitSetting) => {
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
