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
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable, switchMap, tap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  SubmitT4CModel,
  T4CModel,
  T4CModelService,
} from 'src/app/projects/models/model-source/t4c/service/t4c-model.service';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import {
  T4CInstance,
  T4CInstanceService,
} from 'src/app/services/settings/t4c-instance.service';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';

@Component({
  selector: 'app-manage-t4c-model',
  templateUrl: './manage-t4c-model.component.html',
  styleUrls: ['./manage-t4c-model.component.css'],
})
export class ManageT4CModelComponent implements OnInit, OnDestroy {
  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<boolean>();

  editing = false;
  loading = false;

  t4cInstances: T4CInstance[] | undefined = undefined;

  t4cRepositories: T4CRepository[] | undefined = undefined;
  get selectedRepository(): T4CRepository | undefined {
    return this.t4cRepositories?.find(
      (repository: T4CRepository) =>
        repository.id == this.form.value.t4cRepositoryId
    );
  }

  t4cModel?: T4CModel;

  public form = new FormGroup({
    t4cInstanceId: new FormControl<null | number>(null, [Validators.required]),
    t4cRepositoryId: new FormControl<null | number>(null, [
      Validators.required,
    ]),
    name: new FormControl('', [Validators.required]),
  });

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public t4cInstanceService: T4CInstanceService,
    public t4cRepositoryService: T4CRepoService,
    public t4cModelService: T4CModelService,
    private router: Router,
    private route: ActivatedRoute,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.form.disable({ emitEvent: false });
    this.loading = true;
    this.updateRepositoryListOnInstanceChange();
    this.updateProjectListOnRepositoryChange();

    this.fetchT4CInstances()
      .pipe(switchMap(() => this.patchFormWithExistingT4CModel()))
      .subscribe(() => {
        this.loading = false;
      });
  }

  fetchT4CInstances(): Observable<T4CInstance[]> {
    return this.t4cInstanceService.listInstances().pipe(
      tap((instances) => {
        this.t4cInstances = instances;
        this.form.controls.t4cInstanceId.enable({ emitEvent: false });
      })
    );
  }

  updateRepositoryListOnInstanceChange(): void {
    this.form.controls.t4cInstanceId.valueChanges.subscribe(
      (t4cInstanceId: number | null) => {
        if (t4cInstanceId) {
          this.t4cRepositoryService
            .getT4CRepositories(t4cInstanceId)
            .subscribe((repositories) => {
              this.t4cRepositories = repositories;
              this.form.controls.t4cRepositoryId.enable({
                emitEvent: false,
              });
            });
        }
      }
    );
  }

  updateProjectListOnRepositoryChange(): void {
    this.form.controls.t4cRepositoryId.valueChanges.subscribe(() => {
      this.form.controls.name.enable({ emitEvent: false });
    });
  }

  patchFormWithExistingT4CModel(): Observable<T4CModel | undefined> {
    return this.t4cModelService._t4cModel.pipe(
      tap((model: T4CModel | undefined) => {
        if (model) {
          this.editing = true;
          this.t4cModel = model;

          this.form.controls.t4cInstanceId.setValue(
            model.repository.instance.id
          );

          this.form.controls.t4cRepositoryId.patchValue(model.repository.id);
          this.form.controls.name.patchValue(model.name);
          this.form.enable({ emitEvent: false });
        }
      })
    );
  }

  onSubmit() {
    if (this.form.invalid) {
      return;
    }
    if (this.t4cModelService.t4cModel) {
      this.t4cModelService
        .patchT4CModel(
          this.projectService.project!.slug,
          this.modelService.model!.slug,
          this.t4cModelService.t4cModel.id,
          this.form.value as SubmitT4CModel
        )
        .subscribe((model) => {
          this.t4cModelService._t4cModel.next(model);
          this.patchFormWithExistingT4CModel();
          this.toastService.showSuccess(
            'TeamForCapella repository link successfully updated',
            ''
          );
        });
    } else {
      this.t4cModelService
        .createT4CModel(
          this.projectService.project!.slug,
          this.modelService.model!.slug,
          this.form.value as SubmitT4CModel
        )
        .subscribe((_) => {
          if (this.asStepper) {
            this.create.emit(true);
          } else {
            this.router.navigate(['../..'], { relativeTo: this.route });
          }
          this.toastService.showSuccess(
            'TeamForCapella repository successfully linked',
            ''
          );
        });
    }
  }

  ngOnDestroy(): void {
    this.t4cModelService._t4cModel.next(undefined);
  }

  unlinkT4CModel() {
    if (!window.confirm(`Do you really want to unlink this T4C model?`)) {
      return;
    }

    this.t4cModelService
      .unlinkT4CModel(
        this.projectService.project?.slug!,
        this.modelService.model?.slug!,
        this.t4cModel!.id
      )
      .subscribe({
        next: () => {
          this.toastService.showSuccess(
            'T4C model deleted',
            `${this.t4cModel!.name} has been deleted`
          );
          this.router.navigateByUrl(
            `/project/${this.projectService.project?.slug!}/model/${this
              .modelService.model?.slug!}`
          );
        },
        error: () => {
          this.toastService.showError(
            'T4C model deletion failed',
            `${this.t4cModel!.name} has not been deleted`
          );
        },
      });
  }
}
