/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { combineLatest, filter, switchMap } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ProjectService } from 'src/app/projects/service/project.service';
import { T4CInstanceService } from 'src/app/services/settings/t4c-instance.service';
import { T4CRepoService } from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { ModelService } from '../../../service/model.service';
import { T4CModelService } from '../service/t4c-model.service';

@UntilDestroy()
@Component({
  selector: 'app-create-t4c-model-new-repository',
  templateUrl: './create-t4c-model-new-repository.component.html',
  styleUrls: ['./create-t4c-model-new-repository.component.css'],
})
export class CreateT4cModelNewRepositoryComponent implements OnInit {
  @Input() asStepper?: boolean;
  @Output() create = new EventEmitter<boolean>();

  private projectSlug?: string;
  private modelSlug?: string;

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public t4cModelService: T4CModelService,
    public t4cInstanceService: T4CInstanceService,
    private t4cRepoService: T4CRepoService,
    private router: Router,
    private route: ActivatedRoute,
    private toastService: ToastService,
  ) {}

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
            this.router.navigate(['../../modelsources'], {
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
