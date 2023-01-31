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
import { Subject, connectable, switchMap, tap } from 'rxjs';
import slugify from 'slugify';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Model,
  ModelService,
  NewModel,
} from 'src/app/projects/models/service/model.service';
import { ToolService } from 'src/app/settings/core/tools-settings/tool.service';
import { ProjectService } from '../../service/project.service';

@Component({
  selector: 'app-create-model-base',
  templateUrl: './create-model-base.component.html',
  styleUrls: ['./create-model-base.component.css'],
})
export class CreateModelBaseComponent implements OnInit {
  @Output() create = new EventEmitter();
  @Input() asStepper?: boolean;

  public form = new FormGroup({
    name: new FormControl('', [Validators.required, this.slugValidator()]),
    description: new FormControl(''),
    toolID: new FormControl<number | undefined>(undefined, [
      Validators.required,
      this.validToolValidator(),
    ]),
  });

  constructor(
    private modelService: ModelService,
    public projectService: ProjectService,
    public toolService: ToolService,
    private toastService: ToastService
  ) {}

  slugValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const models = this.modelService.models;
      const slug = slugify(control.value, { lower: true });
      if (models && models.find((model) => model.slug == slug)) {
        return { uniqueSlug: { value: slug } };
      }
      return null;
    };
  }

  validToolValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const tools = this.toolService.tools;
      const value = control.value;
      if (!value || (tools && tools.find((tool) => tool.id == value))) {
        return null;
      }
      return { noValidTool: true };
    };
  }

  ngOnInit(): void {
    this.toolService.getTools().subscribe();
    this.modelService._models.subscribe();
    this.modelService._model.next(undefined);
  }

  onSubmit(): void {
    if (this.form.valid && this.projectService.project?.slug) {
      const modelConnectable = connectable<Model>(
        this.modelService.createNewModel(this.projectService.project.slug, {
          name: this.form.value.name,
          description: this.form.value.description,
          tool_id: this.form.value.toolID,
        } as NewModel),
        {
          connector: () => new Subject(),
          resetOnDisconnect: false,
        }
      );

      modelConnectable
        .pipe(
          switchMap((_) =>
            this.modelService.getModels(this.projectService.project!.slug)
          )
        )
        .subscribe((value) => {
          this.modelService._models.next(value);
        });

      modelConnectable
        .pipe(tap((model) => this.modelService._model.next(model)))
        .subscribe({
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
