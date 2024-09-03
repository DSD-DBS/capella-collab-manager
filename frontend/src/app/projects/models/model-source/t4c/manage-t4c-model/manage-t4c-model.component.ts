/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
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
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import {
  MatAutocompleteTrigger,
  MatAutocomplete,
} from '@angular/material/autocomplete';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatDialog } from '@angular/material/dialog';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { MatTooltip } from '@angular/material/tooltip';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter } from 'rxjs';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  SubmitT4CModel,
  T4CModel,
  T4CModelService,
} from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import {
  ExtendedT4CRepository,
  T4CRepositoryWrapperService,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { ButtonSkeletonLoaderComponent } from '../../../../../helpers/skeleton-loaders/button-skeleton-loader/button-skeleton-loader.component';
import { FormFieldSkeletonLoaderComponent } from '../../../../../helpers/skeleton-loaders/form-field-skeleton-loader/form-field-skeleton-loader.component';

@UntilDestroy()
@Component({
  selector: 'app-manage-t4c-model',
  templateUrl: './manage-t4c-model.component.html',
  styleUrls: ['./manage-t4c-model.component.css'],
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    FormFieldSkeletonLoaderComponent,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatTooltip,
    MatError,
    MatInput,
    MatAutocompleteTrigger,
    MatAutocomplete,
    MatButton,
    ButtonSkeletonLoaderComponent,
    MatIcon,
    AsyncPipe,
  ],
})
export class ManageT4CModelComponent implements OnInit, OnDestroy {
  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<boolean>();

  private projectSlug?: string;
  private modelSlug?: string;

  loading = false;

  t4cRepositories?: ExtendedT4CRepository[];

  selectedRepository?: ExtendedT4CRepository;

  t4cModel?: T4CModel;

  constructor(
    public projectService: ProjectWrapperService,
    public modelService: ModelWrapperService,
    public t4cInstanceService: T4CInstanceWrapperService,
    public t4cRepositoryService: T4CRepositoryWrapperService,
    public t4cModelService: T4CModelService,
    private router: Router,
    private route: ActivatedRoute,
    private toastService: ToastService,
    private dialog: MatDialog,
  ) {}

  public form = new FormGroup({
    t4cInstanceId: new FormControl<number | null>(null, Validators.required),
    t4cRepositoryId: new FormControl<number | null>(
      { value: null, disabled: true },
      Validators.required,
    ),
    name: new FormControl({ value: '', disabled: true }, Validators.required),
  });

  ngOnInit(): void {
    this.form.controls.t4cInstanceId.valueChanges
      .pipe(filter(Boolean))
      .subscribe((t4cInstanceId) => {
        this.form.controls.t4cRepositoryId.enable();
        this.t4cRepositoryService.loadRepositories(t4cInstanceId);
      });

    this.form.controls.t4cRepositoryId.valueChanges
      .pipe(filter(Boolean))
      .subscribe((repositoryId) => {
        this.selectedRepository = this.t4cRepositories?.find(
          (repository) => repository.id === repositoryId,
        );

        const instanceId = this.form.value.t4cInstanceId;
        if (instanceId) {
          this.form.controls.name.setAsyncValidators(
            this.t4cModelService.asyncNameValidator(instanceId, repositoryId),
          );
          this.form.controls.name.setValue('');
          this.form.controls.name.enable();
        }
      });

    this.t4cRepositoryService.repositories$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((repositories) => {
        this.t4cRepositories = repositories;
        this.form.controls.t4cRepositoryId.enable({ emitEvent: false });
      });

    this.t4cModelService.t4cModel$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe((t4cModel) => {
        this.t4cModel = t4cModel;

        this.form.controls.t4cInstanceId.patchValue(
          t4cModel.repository.instance.id,
        );
        this.form.controls.t4cRepositoryId.patchValue(t4cModel.repository.id);
        this.form.controls.name.patchValue(t4cModel.name);

        this.form.enable({ emitEvent: false });
      });

    this.t4cInstanceService.loadInstances();

    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model]) => {
        this.projectSlug = project.slug;
        this.modelSlug = model.slug;
        this.t4cModelService.loadT4CModels(project.slug, model.slug);
      });

    this.t4cRepositoryService.repositories$
      .pipe(untilDestroyed(this), filter(Boolean))
      .subscribe(() =>
        this.form.controls.t4cRepositoryId.enable({
          emitEvent: false,
        }),
      );
  }

  ngOnDestroy(): void {
    this.t4cModelService.reset();
    this.t4cRepositoryService.reset();
    this.t4cInstanceService.resetT4CInstance();
  }

  onSubmit() {
    if (this.form.invalid || !this.projectSlug || !this.modelSlug) {
      return;
    }

    const submitModel: SubmitT4CModel = {
      t4c_instance_id: this.form.value.t4cInstanceId!,
      t4c_repository_id: this.form.value.t4cRepositoryId!,
      name: this.form.value.name!,
    };

    if (this.t4cModel) {
      this.t4cModelService
        .patchT4CModel(
          this.projectSlug,
          this.modelSlug,
          this.t4cModel.id,
          submitModel,
        )
        .subscribe(() => {
          this.toastService.showSuccess(
            'TeamForCapella repository link successfully updated',
            '',
          );
        });
    } else {
      this.t4cModelService
        .createT4CModel(this.projectSlug, this.modelSlug, submitModel)
        .subscribe(() => {
          if (this.asStepper) {
            this.create.emit(true);
          } else {
            this.router.navigate(['../../modelsources'], {
              relativeTo: this.route,
            });
          }
          this.toastService.showSuccess(
            'TeamForCapella repository successfully linked',
            `A new TeamForCapella repository was linked to the model '${this.modelSlug}'`,
          );
        });
    }
  }

  unlinkT4CModel() {
    if (!(this.projectSlug && this.modelSlug && this.t4cModel)) {
      return;
    }

    const projectSlug = this.projectSlug!;
    const modelSlug = this.modelSlug!;
    const t4cModel = this.t4cModel!;

    const dialogRef = this.dialog.open(ConfirmationDialogComponent, {
      data: {
        title: 'Unlink T4C Model',
        text: 'Do you really want to unlink this T4C model?',
      },
    });

    dialogRef.afterClosed().subscribe((result: boolean) => {
      if (result) {
        this.t4cModelService
          .unlinkT4CModel(projectSlug, modelSlug, t4cModel.id)
          .subscribe({
            next: () => {
              this.toastService.showSuccess(
                'TeamForCapella project unlinked',
                `The TeamForCapella repository with the name '${t4cModel.name}' has been unlinked`,
              );
              this.router.navigateByUrl(
                `/project/${projectSlug!}/model/${modelSlug}/modelsources`,
              );
            },
          });
      }
    });
  }
}
