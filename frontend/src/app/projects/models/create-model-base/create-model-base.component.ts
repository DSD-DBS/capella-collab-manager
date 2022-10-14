/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

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
import { Subject, connectable, filter, switchMap, tap } from 'rxjs';
import slugify from 'slugify';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Model,
  ModelService,
  NewModel,
} from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';
import { ToolService } from 'src/app/services/tools/tool.service';

@Component({
  selector: 'app-create-model-base',
  templateUrl: './create-model-base.component.html',
  styleUrls: ['./create-model-base.component.css'],
})
export class CreateModelBaseComponent implements OnInit {
  @Output() create = new EventEmitter();
  @Input() asStepper?: boolean;

  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl(''),
    tool_id: new FormControl(-1, this.validToolValidator()),
  });

  constructor(
    private modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService,
    private toastService: ToastService
  ) {}

  slugValidator(slugs: string[]): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const newSlug = slugify(control.value, { lower: true });
      for (const slug of slugs) {
        if (slug == newSlug) {
          return { uniqueSlug: { value: slug } };
        }
      }
      return null;
    };
  }

  validToolValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (this.toolService.tools) {
        for (const tool of this.toolService.tools) {
          if (tool.id == control.value) {
            return null;
          }
        }
      }
      return { noValidTool: true };
    };
  }

  ngOnInit(): void {
    this.toolService.getTools().subscribe();
    this.modelService._models.pipe(filter(Boolean)).subscribe((models) => {
      this.form.controls.name.addValidators(
        this.slugValidator(models.map((model) => model.slug))
      );
    });
    this.modelService._model.next(undefined);
  }

  onSubmit(): void {
    if (this.form.valid && this.projectService.project?.slug) {
      const modelConnectable = connectable<Model>(
        this.modelService.createNewModel(
          this.projectService.project.slug,
          this.form.value as NewModel
        ),
        {
          connector: () => new Subject(),
          resetOnDisconnect: false,
        }
      );

      modelConnectable
        .pipe(
          switchMap((_) =>
            this.modelService.list(this.projectService.project!.slug)
          )
        )
        .subscribe((value) => {
          this.modelService._models.next(value);
        });

      modelConnectable.pipe(tap(this.modelService._model)).subscribe({
        next: (model: Model | undefined) => {
          this.toastService.showSuccess(
            'Model created',
            `The model with name ${model!.name} has been created`
          );
          this.create.emit();
        },
      });

      modelConnectable.connect();
    }
  }
}
