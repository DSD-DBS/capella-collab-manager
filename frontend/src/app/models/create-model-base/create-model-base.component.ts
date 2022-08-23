// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import slugify from 'slugify';
import { ProjectService } from 'src/app/services/project/project.service';
import {
  Model,
  ModelService,
  NewModel,
} from 'src/app/services/model/model.service';
import { ToolService } from 'src/app/services/tools/tool.service';
import { connectable, filter, Subject, switchMap, tap } from 'rxjs';

@Component({
  selector: 'app-create-model-base',
  templateUrl: './create-model-base.component.html',
  styleUrls: ['./create-model-base.component.css'],
})
export class CreateModelBaseComponent implements OnInit {
  @Output() create = new EventEmitter<Model>();
  @Output() finish = new EventEmitter<boolean>();
  @Input() as_stepper?: boolean;

  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
    tool_id: new FormControl('', Validators.required),
  });

  constructor(
    private modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService
  ) {}

  slugValidator(slugs: string[]): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      let new_slug = slugify(control.value, { lower: true });
      for (let slug of slugs) {
        if (slug == new_slug) {
          return { uniqueSlug: { value: slug } };
        }
      }
      return null;
    };
  }

  ngOnInit(): void {
    this.toolService.get_tools().subscribe();
    this.modelService._models.pipe(filter(Boolean)).subscribe((models) => {
      this.form.controls.name.addValidators(
        this.slugValidator(models.map((model) => model.slug))
      );
    });
    this.modelService._model.next(undefined);
  }

  onSubmit(): void {
    if (this.form.valid && this.projectService.project?.slug) {
      let new_model = this.form.value as NewModel;

      const model_creation_subject = connectable<Model>(
        this.modelService
          .createNewModel(this.projectService.project.slug, new_model)
          .pipe(filter((_) => !!this.projectService.project)),
        {
          connector: () => new Subject(),
          resetOnDisconnect: false,
        }
      );

      let models = this.modelService._models;
      model_creation_subject
        .pipe(
          switchMap(() =>
            this.modelService.list(this.projectService.project!.slug)
          )
        )
        .subscribe({
          next: models.next.bind(models),
        });

      model_creation_subject
        .pipe(tap(this.modelService._model))
        .subscribe(this.create.emit.bind(this.create));

      model_creation_subject.connect();
    }
  }
}
