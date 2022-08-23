// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

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
import { Model } from 'src/app/services/model/model.service';

@Component({
  selector: 'app-create-model',
  templateUrl: './create-model.component.html',
  styleUrls: ['./create-model.component.css'],
})
export class CreateModelComponent implements OnInit {
  @ViewChild('stepper') stepper!: MatStepper;
  @Input() as_stepper?: boolean;
  @Output() complete = new EventEmitter<boolean>();

  source?: string;
  init?: string;

  constructor(private router: Router) {}

  ngOnInit(): void {}

  afterModelCreated(model: Model): void {
    console.log(model);
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
    console.log(created);
    if (created) {
      this.stepper.steps.get(2)!.completed = true;
      this.stepper.next();
      this.stepper.steps.get(1)!.editable = false;
      this.stepper.steps.get(2)!.editable = false;
    } else {
      console.log(this.stepper);
      this.stepper.previous();
    }
  }

  onInitClick(value: string): void {
    this.stepper.steps.get(3)!.completed = true;
    this.init = value;
    this.stepper.next();
  }

  afterModelInitialized(created: boolean): void {
    console.log(created);
    if (created) {
      if (this.as_stepper) {
        this.complete.emit(true);
      } else {
        this.router.navigateByUrl('../');
      }
    } else {
      this.stepper.previous();
    }
  }

  handleSelectionChange(): void {}
}
