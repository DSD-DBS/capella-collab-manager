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
} from '@angular/forms';
import {
  T4CInstanceService,
  T4CInstance,
} from 'src/app/services/settings/t4c-model.service';
import {
  T4CRepoService,
  T4CRepository,
} from 'src/app/settings/modelsources/t4c-settings/service/t4c-repos/t4c-repo.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { ModelService } from 'src/app/services/model/model.service';
import { BehaviorSubject, filter, switchMap, tap } from 'rxjs';
import {
  CreateT4CModel,
  T4cModelService,
} from '../../../services/source/t4c-model.service';

@Component({
  selector: 'app-add-t4c-source',
  templateUrl: './add-t4c-source.component.html',
  styleUrls: ['./add-t4c-source.component.css'],
})
export class AddT4cSourceComponent implements OnInit {
  @Output() create = new EventEmitter<boolean>();

  private _instances = new BehaviorSubject<T4CInstance[]>([]);
  get instances() {
    return this._instances.getValue();
  }

  instanceValidator(control: AbstractControl): ValidationErrors | null {
    return this.instances.map((i) => i.id).indexOf(parseInt(control.value)) >= 0
      ? null
      : { error: true };
  }

  private _repositories = new BehaviorSubject<T4CRepository[]>([]);
  get repositories() {
    return this._repositories.getValue();
  }

  repositoryValidator(control: AbstractControl): ValidationErrors | null {
    return this.repositories
      .map((i) => i.id)
      .indexOf(parseInt(control.value)) >= 0
      ? null
      : { error: true };
  }

  public form = new FormGroup({
    t4c_instance_id: new FormControl(null as null | number, [
      Validators.required,
      this.instanceValidator.bind(this),
    ]),
    t4c_repository_id: new FormControl(null as null | number, [
      Validators.required,
      this.repositoryValidator.bind(this),
    ]),
    name: new FormControl({ value: '', disabled: true }, Validators.required),
  });

  constructor(
    public projectService: ProjectService,
    public modelService: ModelService,
    public t4cInstanceService: T4CInstanceService,
    public t4cRepoService: T4CRepoService,
    private t4cModelService: T4cModelService
  ) {}

  ngOnInit(): void {
    this.t4cInstanceService.listInstances().subscribe((instances) => {
      this._instances.next(instances);
    });

    this.form.controls.t4c_instance_id.valueChanges
      .pipe(
        filter(Boolean),
        tap(() => {
          this._repositories.next([]);
        }),
        switchMap((instance_id) =>
          this.t4cRepoService.getT4CRepositories(instance_id)
        )
      )
      .subscribe((repositories) => {
        this._repositories.next(repositories);
      });

    this.form.controls.t4c_repository_id.valueChanges.subscribe(() => {
      this.form.controls.name.reset();
    });

    this.form.controls.t4c_repository_id.valueChanges
      .pipe(filter((value) => this.form.controls.t4c_repository_id.valid))
      .subscribe(() => {
        this.form.controls.name.enable();
      });

    this.form.controls.t4c_repository_id.valueChanges
      .pipe(filter((value) => !this.form.controls.t4c_repository_id.valid))
      .subscribe(() => {
        this.form.controls.name.disable();
      });
  }

  get currentRepo() {
    return this.repositories.filter(
      (r) => r.id == this.form.value.t4c_repository_id
    )[0]?.name;
  }

  onSubmit() {
    if (
      this.form.valid &&
      this.projectService.project &&
      this.modelService.model
    ) {
      this.t4cModelService
        .createT4CModel(
          this.projectService.project.slug,
          this.modelService.model.slug,
          this.form.value as CreateT4CModel
        )
        .subscribe((_) => {
          this.create.emit(true);
        });
    }
  }
}
