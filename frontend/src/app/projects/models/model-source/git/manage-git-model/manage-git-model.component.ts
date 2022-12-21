/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  EventEmitter,
  Input,
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
  AsyncValidatorFn,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { filter, map, Observable, of, Subscription } from 'rxjs';
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
import {
  Credentials,
  GitService,
  Revisions,
} from 'src/app/services/git/git.service';
import { ProjectService } from 'src/app/services/project/project.service';
import {
  GitSetting,
  GitSettingsService,
} from 'src/app/services/settings/git-settings.service';

@Component({
  selector: 'app-manage-git-model',
  templateUrl: './manage-git-model.component.html',
  styleUrls: ['./manage-git-model.component.css'],
})
export class ManageGitModelComponent implements OnInit, OnDestroy {
  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<boolean>();

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

  private gitModelId?: number;
  public gitModel?: GetGitModel;

  public isEditMode: boolean = false;
  public editing: boolean = false;

  private gitSettingsSubscription?: Subscription;
  private modelSubscription?: Subscription;
  private revisionsSubscription?: Subscription;
  private gitModelSubscription?: Subscription;
  private paramSubscription?: Subscription;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    private gitSettingsService: GitSettingsService,
    private gitService: GitService,
    private gitModelService: GitModelService,
    private toastService: ToastService,
    private router: Router,
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
          this.urls.inputUrl.setValidators([absoluteOrRelativeValidators()]);
          this.form.controls.urls.setAsyncValidators([
            this.resultUrlPrefixAsyncValidator(),
          ]);
        } else {
          this.urls.inputUrl.addValidators([Validators.required]);
        }
      });

    this.modelSubscription = this.modelService._model.subscribe((model) => {
      if (model?.tool.name === 'Capella') {
        this.form.controls.entrypoint.addValidators(
          Validators.pattern(/^$|\.aird$/)
        );
      }
    });

    this.paramSubscription = this.route.params
      .pipe(
        filter((params) => !!params['git-model']),
        map((params) => params['git-model'])
      )
      .subscribe((gitModelId) => {
        this.isEditMode = true;
        this.gitModelId = gitModelId;
        this.form.disable();

        this.gitModelSubscription = this.gitModelService.gitModel.subscribe(
          (gitModel) => {
            this.gitModel = gitModel;
            this.fillFormWithGitModel(gitModel!);

            this.gitService.loadPrivateRevisions(
              gitModel!.path,
              this.projectService.project?.slug!,
              this.modelService.model?.slug!,
              gitModelId
            );
          }
        );

        this.gitModelService.loadGitModelById(
          this.projectService.project!.slug,
          this.modelService.model!.slug,
          gitModelId
        );
      });

    this.gitSettingsService.loadGitSettings();
  }

  ngOnDestroy(): void {
    this.gitSettingsSubscription?.unsubscribe();
    this.modelSubscription?.unsubscribe();
    this.revisionsSubscription?.unsubscribe();
    this.gitModelSubscription?.unsubscribe();
    this.paramSubscription?.unsubscribe();
  }

  onRevisionFocus(): void {
    if (this.form.controls.urls.valid) {
      if (
        this.isEditMode &&
        !this.form.controls.credentials.controls.password.value
      ) {
        this.gitService.loadPrivateRevisions(
          this.resultUrl,
          this.projectService.project?.slug!,
          this.modelService.model?.slug!,
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

  onBaseIntegrationUrlSelect(value: GitSetting): void {
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

    if (!this.availableGitInstances.length) {
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
      } else if (this.availableGitInstances.length) {
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
          this.projectService.project?.slug!,
          this.modelService.model?.slug!,
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
          this.projectService.project?.slug!,
          this.modelService.model?.slug!,
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
      .deleteGitSource(
        this.projectService.project?.slug!,
        this.modelService.model?.slug!,
        this.gitModel!
      )
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'Git model deleted',
            `${this.gitModel!.path} has been deleted`
          );
          this.router.navigateByUrl(
            `/project/${this.projectService.project?.slug!}/model/${this
              .modelService.model?.slug!}`
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
        .validatePath(
          this.projectService.project?.slug!,
          this.modelService.model?.slug!,
          this.resultUrl
        )
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
