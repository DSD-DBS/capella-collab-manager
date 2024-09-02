/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgIf, NgFor, AsyncPipe } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import {
  Validators,
  ValidationErrors,
  AbstractControl,
  AsyncValidatorFn,
  FormBuilder,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import {
  MatAutocompleteTrigger,
  MatAutocomplete,
} from '@angular/material/autocomplete';
import { MatButton } from '@angular/material/button';
import { MatOption, MatOptgroup } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import {
  MatFormField,
  MatLabel,
  MatError,
  MatHint,
} from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { MatSlideToggle } from '@angular/material/slide-toggle';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { filter, map, Observable, of } from 'rxjs';
import { BreadcrumbsService } from 'src/app/general/breadcrumbs/breadcrumbs.service';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  absoluteOrRelativeValidators,
  absoluteUrlValidator,
  hasAbsoluteUrlPrefix,
  hasRelativePathPrefix,
} from 'src/app/helpers/validators/url-validator';
import { SettingsModelsourcesGitService } from 'src/app/openapi';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import {
  CreateGitModel,
  GetGitModel,
  GitModelService,
  PatchGitModel,
} from 'src/app/projects/project-detail/model-overview/model-detail/git-model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
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
  standalone: true,
  imports: [
    NgIf,
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatSelect,
    NgFor,
    MatOption,
    MatError,
    MatInput,
    MatIcon,
    MatHint,
    MatAutocompleteTrigger,
    MatAutocomplete,
    MatOptgroup,
    MatSlideToggle,
    MatButton,
    AsyncPipe,
  ],
})
export class ManageGitModelComponent implements OnInit, OnDestroy {
  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<boolean>();

  public availableGitInstances?: Array<GitInstance>;
  public selectedGitInstance?: GitInstance;

  private revisions?: Revisions;
  public filteredRevisions?: Revisions;

  public resultUrl = '';

  private projectSlug?: string = undefined;
  private modelSlug?: string = undefined;

  private gitModelId?: number;
  public gitModel?: GetGitModel;

  public isEditMode = false;
  public editing = false;

  constructor(
    public projectService: ProjectWrapperService,
    public modelService: ModelWrapperService,
    private gitInstancesService: GitInstancesService,
    private settingsModelsourcesGitService: SettingsModelsourcesGitService,
    private gitService: GitService,
    private gitModelService: GitModelService,
    private toastService: ToastService,
    private breadCrumbsService: BreadcrumbsService,
    private router: Router,
    private route: ActivatedRoute,
    private fb: FormBuilder,
    private dialog: MatDialog,
  ) {}

  public form = this.fb.group({
    urls: this.fb.group({
      baseUrl: this.fb.control<GitInstance | undefined>(undefined),
      inputUrl: this.fb.control('', absoluteUrlValidator()),
    }),
    credentials: this.fb.group({
      username: this.fb.control({ value: '', disabled: true }),
      password: this.fb.control({ value: '', disabled: true }),
    }),
    revision: this.fb.control(
      { value: '', disabled: true },
      {
        validators: Validators.required,
        asyncValidators: this.gitService.asyncExistingRevisionValidator(),
      },
    ),
    entrypoint: this.fb.control({ value: '/', disabled: true }),
    primary: this.fb.control(false),
  });

  get urls() {
    return this.form.controls.urls.controls;
  }

  ngOnInit(): void {
    this.gitService.revisions$.pipe(untilDestroyed(this)).subscribe({
      next: (revisions) => {
        this.revisions = revisions;
        this.filteredRevisions = revisions;
        this.form.controls.revision.updateValueAndValidity();
      },
      complete: () => this.gitService.clearRevision(),
    });

    this.form.controls.revision.valueChanges.subscribe((value) =>
      this.filteredRevisionsByPrefix(value as string),
    );

    this.gitInstancesService.gitInstances$
      .pipe(untilDestroyed(this))
      .subscribe((gitInstances) => {
        this.availableGitInstances = gitInstances;

        if (gitInstances?.length) {
          this.urls.baseUrl.setValidators([Validators.required]);
          this.urls.inputUrl.setValidators([absoluteOrRelativeValidators()]);
          this.form.controls.urls.setAsyncValidators([
            this.resultUrlPrefixAsyncValidator(),
          ]);
        } else {
          this.urls.inputUrl.addValidators([Validators.required]);
        }
      });

    this.modelService.model$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((model) => {
        this.modelSlug = model.slug;
        if (model.tool.name === 'Capella') {
          this.form.controls.entrypoint.addValidators([
            Validators.pattern(/^$|\.aird$/),
            Validators.required,
          ]);
        }
      });

    this.projectService.project$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((project) => {
        this.projectSlug = project.slug;

        this.route.params
          .pipe(
            filter((params) => !!params['git-model']),
            map((params) => params['git-model']),
          )
          .subscribe((gitModelId) => {
            this.isEditMode = true;
            this.gitModelId = gitModelId;
            this.form.disable();

            this.gitModelService.gitModel$
              .pipe(untilDestroyed(this), filter(Boolean))
              .subscribe((gitModel) => {
                this.gitModel = gitModel;
                this.fillFormWithGitModel(gitModel);

                this.breadCrumbsService.updatePlaceholder({ gitModel });

                this.gitService.loadPrivateRevisions(
                  gitModel.path,
                  this.projectSlug!,
                  this.modelSlug!,
                  gitModelId,
                );
              });

            this.gitModelService.loadGitModelById(
              this.projectSlug!,
              this.modelSlug!,
              gitModelId,
            );
          });
      });

    this.gitInstancesService.loadGitInstances();
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
          this.gitModelId!,
        );
      } else {
        this.gitService.loadRevisions(
          this.resultUrl,
          this.form.value.credentials as Credentials,
        );
      }
    }
  }

  onBaseIntegrationUrlSelect(value: GitInstance): void {
    const inputUrlControl = this.urls.inputUrl;
    const inputUrl = inputUrlControl.value;

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
      const longestMatchingGitInstance =
        this.findLongestUrlMatchingGitInstance(changedInputUrl);
      if (longestMatchingGitInstance) {
        this.selectedGitInstance = longestMatchingGitInstance;
        this.urls.baseUrl.setValue(longestMatchingGitInstance);
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
          this.createGitModelFromForm(),
        )
        .subscribe(() => {
          if (this.asStepper) {
            this.create.emit(true);
          } else {
            this.router.navigate(['../../modelsources'], {
              relativeTo: this.route,
            });
          }
        });
    }
  }

  onEditSubmit(): void {
    if (this.form.valid) {
      const patchGitModel = this.createGitModelFromForm() as PatchGitModel;
      patchGitModel.primary = this.form.controls.primary.value!;

      this.gitModelService
        .updateGitRepository(
          this.projectSlug!,
          this.modelSlug!,
          this.gitModelId!,
          patchGitModel,
        )
        .subscribe(() =>
          this.router.navigate(['../../modelsources'], {
            relativeTo: this.route,
          }),
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
    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Unlink Git Model',
        text: 'Do you really want to unlink this Git model?',
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.gitModelService
          .deleteGitSource(this.projectSlug!, this.modelSlug!, this.gitModel!)
          .subscribe({
            next: () => {
              this.toastService.showSuccess(
                'Git repository unlinked',
                `The Git repository '${this.gitModel!.path}' has been unlinked`,
              );
              this.router.navigateByUrl(
                `/project/${this.projectSlug!}/model/${this
                  .modelSlug!}/modelsources`,
              );
            },
          });
      }
    });
  }

  private createGitModelFromForm(): CreateGitModel {
    return {
      path: this.resultUrl,
      revision: this.form.value.revision!,
      entrypoint: this.form.value.entrypoint!,
      username: this.form.value.credentials!.username!,
      password: this.form.value.credentials!.password!,
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

  filteredRevisionsByPrefix(prefix: string): void {
    if (!this.revisions) {
      this.filteredRevisions = undefined;
      return;
    }

    this.filteredRevisions = {
      branches: this.revisions!.branches.filter((branch) =>
        branch.toLowerCase().startsWith(prefix.toLowerCase()),
      ),
      tags: this.revisions!.tags.filter((tag) =>
        tag.toLowerCase().startsWith(prefix.toLowerCase()),
      ),
    };
  }

  private resetRevisions() {
    this.revisions = undefined;
    this.filteredRevisions = undefined;
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

      return this.settingsModelsourcesGitService
        .validatePath({ url: this.resultUrl })
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
          }),
        );
    };
  }

  private updateResultUrl() {
    const baseUrl = this.selectedGitInstance?.url || '';
    const inputUrl = this.urls.inputUrl.value!;

    if (hasAbsoluteUrlPrefix(inputUrl)) {
      this.resultUrl = inputUrl;
    } else {
      this.resultUrl = baseUrl + inputUrl;
    }
  }

  private findLongestUrlMatchingGitInstance(
    url: string,
  ): GitInstance | undefined {
    let longestMatchingGitInstance = undefined;
    let longestUrlLength = 0;
    this.availableGitInstances?.forEach((gitInstance) => {
      if (
        url.startsWith(gitInstance.url) &&
        gitInstance.url.length > longestUrlLength
      ) {
        longestMatchingGitInstance = gitInstance;
        longestUrlLength = gitInstance.url.length;
      }
    });

    return longestMatchingGitInstance;
  }
}
