/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { StepperSelectionEvent } from '@angular/cdk/stepper';
import { NgClass, NgSwitch, NgSwitchCase } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { MatStepper, MatStep, MatStepLabel } from '@angular/material/stepper';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { ModelWrapperService } from 'src/app/projects/models/service/model.service';
import { ProjectWrapperService } from '../../service/project.service';
import { CreateModelBaseComponent } from '../create-model-base/create-model-base.component';
import { InitModelComponent } from '../init-model/init-model.component';
import { ChooseSourceComponent } from '../model-source/choose-source.component';
import { ManageGitModelComponent } from '../model-source/git/manage-git-model/manage-git-model.component';
import { CreateT4cModelNewRepositoryComponent } from '../model-source/t4c/create-t4c-model-new-repository/create-t4c-model-new-repository.component';
import { ManageT4CModelComponent } from '../model-source/t4c/manage-t4c-model/manage-t4c-model.component';

@UntilDestroy()
@Component({
  selector: 'app-create-model',
  templateUrl: './create-model.component.html',
  standalone: true,
  imports: [
    MatStepper,
    NgClass,
    MatStep,
    MatStepLabel,
    CreateModelBaseComponent,
    ChooseSourceComponent,
    NgSwitch,
    NgSwitchCase,
    ManageGitModelComponent,
    ManageT4CModelComponent,
    CreateT4cModelNewRepositoryComponent,
    InitModelComponent,
  ],
})
export class CreateModelComponent implements OnInit {
  @ViewChild('stepper') stepper!: MatStepper;
  @Input() asStepper?: boolean;
  @Input() redirectAfterCompletion = true;
  @Output() currentStep = new EventEmitter<CreateModelStep>();

  private projectSlug?: string = undefined;

  source?: string;
  chosenModelInitOption?: string;
  detail?: boolean;

  constructor(
    private router: Router,
    private projectService: ProjectWrapperService,
    private modelService: ModelWrapperService,
  ) {}

  ngOnInit(): void {
    this.projectService.project$
      .pipe(untilDestroyed(this))
      .subscribe((project) => (this.projectSlug = project?.slug));
  }

  onStepChange(event: StepperSelectionEvent) {
    const steps: CreateModelStep[] = [
      'create-model',
      'choose-source',
      'add-source',
      'choose-init',
      'metadata',
    ];
    this.currentStep.emit(steps.at(event.selectedIndex));
  }

  afterModelCreated(): void {
    this.stepper.steps.get(0)!.completed = true;
    this.stepper.next();
    this.stepper.steps.get(0)!.editable = false;
  }

  onSourceClick(value: string): void {
    this.stepper.steps.get(1)!.completed = true;
    if (value === 'skip') {
      this.stepper.next();
      this.stepper.steps.get(2)!.completed = true;
    }
    this.source = value;
    this.stepper.next();
  }

  afterSourceCreated(created: boolean): void {
    if (created) {
      this.stepper.steps.get(2)!.completed = true;
      this.stepper.next();
      this.stepper.steps.get(1)!.editable = false;
      this.stepper.steps.get(2)!.editable = false;
    } else {
      this.stepper.previous();
    }
  }

  onInitClick(value: string): void {
    this.stepper.steps.get(3)!.completed = true;
    this.chosenModelInitOption = value;
    this.stepper.next();
  }

  afterModelInitialized(options: { created: boolean }): void {
    if (options.created) {
      this.currentStep.emit('complete');
      if (this.redirectAfterCompletion) {
        this.modelService.clearModel();
        this.router.navigate(['/project', this.projectSlug!]);
      }
    } else {
      this.stepper.previous();
    }
  }

  hasRoute(route: string) {
    return this.router.url.includes(route);
  }
}

export type CreateModelStep =
  | 'create-model'
  | 'choose-source'
  | 'add-source'
  | 'choose-init'
  | 'metadata'
  | 'complete';
