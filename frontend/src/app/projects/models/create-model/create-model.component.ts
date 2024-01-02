/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { StepperSelectionEvent } from '@angular/cdk/stepper';
import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { MatStepper } from '@angular/material/stepper';
import { Router } from '@angular/router';
import { UntilDestroy, untilDestroyed } from '@ngneat/until-destroy';
import { ModelService } from 'src/app/projects/models/service/model.service';
import { ProjectService } from '../../service/project.service';

@UntilDestroy()
@Component({
  selector: 'app-create-model',
  templateUrl: './create-model.component.html',
  styleUrls: ['./create-model.component.css'],
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
    private projectService: ProjectService,
    private modelService: ModelService,
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
