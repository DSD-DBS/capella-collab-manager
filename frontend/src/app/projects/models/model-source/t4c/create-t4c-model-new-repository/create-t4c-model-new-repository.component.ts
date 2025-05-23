/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { AsyncPipe } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  inject,
} from '@angular/core';
import {
  FormControl,
  FormGroup,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput, MatInputModule } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, switchMap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ProjectWrapperService } from 'src/app/projects/service/project.service';
import { T4CInstanceWrapperService } from 'src/app/services/settings/t4c-instance.service';
import { T4CRepositoryWrapperService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { FormFieldSkeletonLoaderComponent } from '../../../../../helpers/skeleton-loaders/form-field-skeleton-loader/form-field-skeleton-loader.component';
import { ModelWrapperService } from '../../../service/model.service';
import { T4CModelService } from '../service/t4c-model.service';

@UntilDestroy()
@Component({
  selector: 'app-create-t4c-model-new-repository',
  templateUrl: './create-t4c-model-new-repository.component.html',
  imports: [
    FormsModule,
    ReactiveFormsModule,
    FormFieldSkeletonLoaderComponent,
    MatFormField,
    MatLabel,
    MatSelect,
    MatOption,
    MatInput,
    MatError,
    MatButton,
    MatIcon,
    AsyncPipe,
    MatInputModule,
  ],
})
export class CreateT4cModelNewRepositoryComponent implements OnInit {
  projectService = inject(ProjectWrapperService);
  modelService = inject(ModelWrapperService);
  t4cModelService = inject(T4CModelService);
  t4cInstanceService = inject(T4CInstanceWrapperService);
  private t4cRepoService = inject(T4CRepositoryWrapperService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private toastService = inject(ToastService);

  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<boolean>();

  private projectSlug?: string;
  private modelSlug?: string;

  public form = new FormGroup({
    t4cInstanceId: new FormControl<number | null>(null, Validators.required),
    t4cRepositoryName: new FormControl<string | null>(
      { value: null, disabled: true },
      {
        validators: [
          Validators.required,
          Validators.pattern(/^[-a-zA-Z0-9_]+$/),
        ],
        asyncValidators: this.t4cRepoService.asyncNameValidator(),
      },
    ),
    t4cProjectName: new FormControl<string | null>(
      { value: null, disabled: true },
      Validators.required,
    ),
  });

  get t4cRepositoryNameControl() {
    return this.form.controls.t4cRepositoryName;
  }

  get t4cProjectNameControl() {
    return this.form.controls.t4cProjectName;
  }

  ngOnInit(): void {
    this.t4cInstanceService.loadInstances();

    combineLatest([
      this.projectService.project$.pipe(filter(Boolean)),
      this.modelService.model$.pipe(filter(Boolean)),
    ])
      .pipe(untilDestroyed(this))
      .subscribe(([project, model]) => {
        this.projectSlug = project.slug;
        this.modelSlug = model.slug;
      });

    this.form.controls.t4cInstanceId.valueChanges.subscribe(
      (selectedInstanceId) => {
        if (selectedInstanceId) {
          this.t4cRepoService.loadRepositories(selectedInstanceId);

          this.t4cRepositoryNameControl.setValue(null);
          this.t4cRepositoryNameControl.enable();

          this.t4cProjectNameControl.setValue(null);
          this.t4cProjectNameControl.enable();
        }
      },
    );

    this.t4cRepositoryNameControl.valueChanges.subscribe((value) => {
      this.t4cProjectNameControl.setValue(value);
    });
  }

  onSubmit(): void {
    const projectSlug = this.projectSlug;
    const modelSlug = this.modelSlug;

    if (this.form.valid && projectSlug && modelSlug) {
      const t4cInstanceId = this.form.value.t4cInstanceId!;
      const t4cRepositoryName = this.form.value.t4cRepositoryName!;
      const t4cProjectName = this.form.value.t4cProjectName!;

      this.t4cRepoService
        .createRepository(t4cInstanceId, {
          name: t4cRepositoryName,
        })
        .pipe(
          switchMap((repository) =>
            this.t4cModelService.createT4CModel(projectSlug, modelSlug, {
              t4c_instance_id: t4cInstanceId,
              t4c_repository_id: repository.id,
              name: t4cProjectName,
            }),
          ),
        )
        .subscribe(() => {
          if (this.asStepper) {
            this.create.emit(true);
          } else {
            this.router.navigate(['../..'], {
              relativeTo: this.route,
            });
          }
          this.toastService.showSuccess(
            'TeamForCapella repository successfully created and linked',
            `A new TeamForCapella repository was created and linked to the model '${this.modelSlug}'`,
          );
        });
    }
  }
}
