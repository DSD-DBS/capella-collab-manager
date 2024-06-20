/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NgIf, NgFor, AsyncPipe } from '@angular/common';
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
  FormsModule,
  ReactiveFormsModule,
} from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatOption } from '@angular/material/core';
import { MatFormField, MatLabel, MatError } from '@angular/material/form-field';
import { MatIcon } from '@angular/material/icon';
import { MatInput } from '@angular/material/input';
import { MatSelect } from '@angular/material/select';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ToolWrapperService } from 'src/app/settings/core/tools-settings/tool.service';
import { ProjectWrapperService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-create-model-base',
  templateUrl: './create-model-base.component.html',
  styleUrls: ['./create-model-base.component.css'],
  standalone: true,
  imports: [
    NgIf,
    FormsModule,
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatError,
    MatSelect,
    NgFor,
    MatOption,
    MatButton,
    MatIcon,
    AsyncPipe,
  ],
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
    private modelService: ModelWrapperService,
    public projectService: ProjectWrapperService,
    public toolWrapperService: ToolWrapperService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.toolWrapperService.getTools().subscribe();
    this.modelService.clearModel();

    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) => (this.projectSlug = project?.slug));
  }

  onSubmit(): void {
    if (this.form.valid && this.projectSlug) {
      this.modelService
        .createModel(this.projectSlug, {
          name: this.form.value.name!,
          description: this.form.value.description,
          tool_id: this.form.value.toolID!,
        })
        .subscribe({
          next: (model) => {
            this.toastService.showSuccess(
              'Model created',
              `The model with name ${model.name} has been created`,
            );
            this.create.emit();
          },
        });
    }
  }

  validToolValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const tools = this.toolWrapperService.tools;
      const value = control.value;
      if (!value || (tools && tools.find((tool) => tool.id == value))) {
        return null;
      }
      return { noValidTool: true };
    };
  }
}
