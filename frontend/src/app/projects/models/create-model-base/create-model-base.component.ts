/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  ModelService,
  NewModel,
} from 'src/app/projects/models/service/model.service';
import { ToolService } from 'src/app/settings/core/tools-settings/tool.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-create-model-base',
  templateUrl: './create-model-base.component.html',
  styleUrls: ['./create-model-base.component.css'],
})
export class CreateModelBaseComponent implements OnInit {
  @Output() create = new EventEmitter();
  @Input() asStepper?: boolean;

  private projectSlug?: string = undefined;

  public form = new FormGroup({
    name: new FormControl('', {
      validators: Validators.required,
      asyncValidators: this.modelService.asyncSlugValidator(),
    }),
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
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.toolService.getTools().subscribe();
    this.modelService.clearModel();

    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) => (this.projectSlug = project?.slug));
  }

  onSubmit(): void {
    if (this.form.valid && this.projectSlug) {
      this.modelService
        .createModel(this.projectSlug, {
          name: this.form.value.name,
          description: this.form.value.description,
          tool_id: this.form.value.toolID,
        } as NewModel)
        .subscribe({
          next: (model) => {
            this.toastService.showSuccess(
              'Model created',
              `The model with name ${model!.name} has been created`,
            );
            this.create.emit();
          },
        });
    }
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
}
