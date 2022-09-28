/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import {
  Component,
  EventEmitter,
  Input,
  OnDestroy,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { MatStepper } from '@angular/material/stepper';
import { Router } from '@angular/router';
import { Model, ModelService } from 'src/app/services/model/model.service';
import { ProjectService } from 'src/app/services/project/project.service';

@Component({
  selector: 'app-create-model',
  templateUrl: './create-model.component.html',
  styleUrls: ['./create-model.component.css'],
})
export class CreateModelComponent implements OnInit, OnDestroy {
  @ViewChild('stepper') stepper!: MatStepper;
  @Input() asStepper?: boolean;
  @Output() complete = new EventEmitter<boolean>();

  source?: string;
  choosen_init?: string;
  detail?: boolean;

  constructor(
    private router: Router,
    private projectService: ProjectService,
    private modelService: ModelService
  ) {}

  ngOnInit(): void {}

  ngOnDestroy(): void {
    if (!this.detail) {
      this.modelService._model.next(undefined);
    }
  }

  afterModelCreated(model: Model): void {
    this.stepper.steps.get(0)!.completed = true;
    this.stepper.next();
    this.stepper.steps.get(0)!.editable = false;
  }

  onSourceClick(value: string): void {
    this.stepper.steps.get(1)!.completed = true;
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
    this.choosen_init = value;
    this.stepper.next();
  }

  afterModelInitialized(options: { created: boolean; again?: boolean }): void {
    if (options.created) {
      if (this.asStepper) {
        this.complete.emit(options.again);
      } else {
        this.detail = true;
        this.router.navigate([
          '/project',
          this.projectService.project!.slug,
          'model',
          this.modelService.model!.slug,
        ]);
      }
    } else {
      this.stepper.previous();
    }
  }
}
