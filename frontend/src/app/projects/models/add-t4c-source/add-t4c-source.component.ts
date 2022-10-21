/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  Validators,
  FormControlStatus,
} from '@angular/forms';
import {
  T4CInstanceService,
  T4CInstance,
  T4CInstanceWithRepository,
} from 'src/app/services/settings/t4c-model.service';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { Model, ModelService } from 'src/app/services/model/model.service';
import {
  BehaviorSubject,
  filter,
  combineLatest,
  switchMap,
  tap,
  map,
  Observable,
  take,
  delay,
} from 'rxjs';
import {
  SubmitT4CModel,
  T4CModel,
  T4cModelService,
} from '../../../services/source/t4c-model.service';

@Component({
  selector: 'app-add-t4c-source',
  templateUrl: './add-t4c-source.component.html',
  styleUrls: ['./add-t4c-source.component.css'],
})
export class AddT4cSourceComponent implements OnInit {
  @Output() create = new EventEmitter<boolean>();

  editing = false;

  private _instances = new BehaviorSubject<T4CInstance[] | undefined>(
    undefined
  );
  get instances() {
    return this._instances.getValue() || [];
  }
  get instance(): T4CInstance | undefined {
    return this.instances.filter(
      (i) => i.id === this.form.value.t4c_instance_id
    )[0];
  }
  private _repositories = new BehaviorSubject<T4CRepository[] | undefined>(
    undefined
  );
  get repositories() {
    return this._repositories.getValue() || [];
  }
  get repository(): T4CRepository | undefined {
    return this.repositories.filter(
      (r) => r.id === this.form.value.t4c_repository_id
    )[0];
  }
  private _models = new BehaviorSubject<T4CModel[] | undefined>(undefined);
  get models() {
    return this._models.getValue() || [];
  }

  instanceValidator(control: AbstractControl): ValidationErrors | null {
    if (!this._instances.getValue()) return null;
    return this.instances.map((i) => i.id).indexOf(parseInt(control.value)) >= 0
      ? null
      : { error: true };
  }

  repositoryValidator(control: AbstractControl): ValidationErrors | null {
    if (!this._repositories.getValue()) return null;
    return this.repositories
      .map((r) => r.id)
      .indexOf(parseInt(control.value)) >= 0
      ? null
      : { error: true };
  }

  uniqueNameValidator(control: AbstractControl): ValidationErrors | null {
    if (!this._models.getValue()) return null;
    return this.models.map((m) => m.name).indexOf(control.value) >= 0
      ? { alreadyUsed: true }
      : null;
  }

  public form = new FormGroup({
    t4c_instance_id: new FormControl(null as null | number, [
      Validators.required,
      this.instanceValidator.bind(this),
    ]),
    t4c_repository_id: new FormControl(
      {
        value: null as null | number,
        disabled: true,
      },
      [Validators.required, this.repositoryValidator.bind(this)]
    ),
    name: new FormControl(
      {
        value: '',
        disabled: true,
      },
      [Validators.required, this.uniqueNameValidator.bind(this)]
    ),
  });

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public t4cInstanceService: T4CInstanceService,
    public t4cRepositoryService: T4CRepoService,
    public t4cModelService: T4cModelService
  ) {}

  ngOnInit(): void {
    this.t4cInstanceService.listInstances().subscribe((instances) => {
      this._instances.next(instances);
    });

    this.form.controls.t4c_instance_id.valueChanges
      .pipe(tap((value) => console.log('new value', value)))
      .subscribe((t4c_instance_id) => {
        this.form.controls.t4c_repository_id.reset();
        if (this.form.controls.t4c_instance_id.valid) {
          this._repositories.next(undefined);
          this.t4cRepositoryService
            .getT4CRepositories(t4c_instance_id!)
            .subscribe((repositories) => {
              this._repositories.next(repositories);
              this.form.controls.t4c_repository_id.enable();
            });
        } else {
          this._repositories.next(undefined);
          this.form.controls.t4c_repository_id.disable();
        }
      });

    this.form.controls.t4c_repository_id.valueChanges.subscribe(
      (t4c_repository_id) => {
        this.form.controls.name.reset();
        if (this.form.controls.t4c_repository_id.valid) {
          this._models.next(undefined);
          this.t4cModelService
            .listT4CModels(
              this.projectService.project!.slug,
              this.modelService.model!.slug,
              this.form.value.t4c_instance_id!,
              t4c_repository_id!
            )
            .subscribe((models) => {
              this._models.next(models);
              this.form.controls.name.enable();
            });
        } else {
          this._models.next([]);
          this.form.controls.name.disable();
        }
      }
    );

    this.resetToInstance();
  }

  onEditing() {
    this.editing = true;
    this.form.enable({ emitEvent: false });
  }

  resetToInstance() {
    this.editing = false;
    this.t4cModelService._t4cModel
      .pipe(filter(Boolean), tap(console.log), take(1))
      .subscribe((model: T4CModel) => {
        console.log('in reset instance', model.repository.instance.id);
        this.form.controls.t4c_instance_id.patchValue(
          model.repository.instance.id
        );

        this._repositories
          .pipe(filter(Boolean), delay(50), take(1))
          .subscribe((repositories) => {
            this.form.controls.t4c_repository_id.patchValue(
              model.repository.id
            );
            this._models
              .pipe(filter(Boolean), delay(50), take(1))
              .subscribe((models) => {
                this.form.controls.name.patchValue(model.name);
                this.form.disable({ emitEvent: false });
              });
          });
      });
  }

  onSubmit() {
    if (
      this.form.valid &&
      this.projectService.project &&
      this.modelService.model
    ) {
      if (this.t4cModelService.t4cModel) {
        this.t4cModelService
          .patchT4CModel(
            this.projectService.project.slug,
            this.modelService.model.slug,
            this.t4cModelService.t4cModel.id,
            this.form.value as SubmitT4CModel
          )
          .subscribe((model) => {
            this.t4cModelService._t4cModel.next(model);
            this.resetToInstance();
          });
      } else {
        this.t4cModelService
          .createT4CModel(
            this.projectService.project.slug,
            this.modelService.model.slug,
            this.form.value as SubmitT4CModel
          )
          .subscribe((_) => {
            this.create.emit(true);
          });
      }
    }
  }
}
