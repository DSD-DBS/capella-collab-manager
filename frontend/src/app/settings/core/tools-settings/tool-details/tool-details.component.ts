/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component } from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { filter, map, switchMap, tap } from 'rxjs';
import { NavBarService } from 'src/app/general/navbar/service/nav-bar.service';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  Tool,
  ToolDockerimages,
  ToolService,
} from '../tool.service';

@Component({
  selector: 'app-tool-details',
  templateUrl: './tool-details.component.html',
  styleUrls: ['./tool-details.component.css'],
})
export class ToolDetailsComponent {
  editing: boolean = false;
  existing: boolean = false;

  selectedTool: Tool | undefined;
  dockerimages: ToolDockerimages | undefined;

  public form = new FormGroup({
    name: new FormControl('', Validators.required),
    dockerimages: new FormGroup({
      persistent: new FormControl('', [
        Validators.required,
        Validators.maxLength(4096),
        this.validDockerImageNameValidator(),
      ]),
      readonly: new FormControl('', [
        Validators.required,
        Validators.maxLength(4096),
        this.validDockerImageNameValidator(),
      ]),
    }),
  });

  constructor(
    private route: ActivatedRoute,
    private navBarService: NavBarService,
    private toolService: ToolService,
    private toastService: ToastService,
    private router: Router
  ) {
    this.route.params
      .pipe(
        map((params) => params.instance),
        filter((instance) => instance === undefined)
      )
      .subscribe({
        next: () => (this.navBarService.title = 'Settings / Tools / Create'),
      });
  }

  enableEditing(): void {
    this.editing = true;
    this.form.enable();
  }

  cancelEditing(): void {
    this.editing = false;
    this.form.disable();
  }

  validDockerImageNameValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      /*
        Name components may contain lowercase letters, digits and separators.
        A separator is defined as a period, one or two underscores, or one or more dashes.
        A name component may not start or end with a separator.

        https://docs.docker.com/engine/reference/commandline/tag/#extended-description

        In addition, we allow $ (to use the $version syntax) and : for the tag.
      */
      if (
        control.value &&
        !/^[a-zA-Z0-9][a-zA-Z0-9_\-/\.:\$]*$/.test(control.value)
      ) {
        return { validDockerImageNameInvalid: true };
      }
      return {};
    };
  }

  create(): void {
    if (this.form.valid) {
      const name = this.form.controls.name.value!;

      this.toolService
        .createTool(name)
        .pipe(
          tap((tool) => {
            this.toastService.showSuccess(
              'Tool created',
              `The tool with name ${tool.name} was created.`
            );

            this.selectedTool = tool;
          }),
          switchMap((tool) => {
            return this.toolService.updateDockerimagesForTool(
              tool.id,
              this.form.controls.dockerimages.value as ToolDockerimages
            );
          }),
          tap((_) => {
            this.toastService.showSuccess(
              'Docker images updated',
              `The Docker images for the tool '${name}' were updated.`
            );
          })
        )
        .subscribe(() => {
          this.router.navigate(['../..', 'tool', this.selectedTool?.id], {
            relativeTo: this.route,
          });
        });
    }
  }

  update(): void {
    if (this.form.valid) {
      this.toolService
        .updateTool(this.selectedTool!.id, this.form.controls.name.value!)
        .pipe(
          tap((tool) => {
            this.toastService.showSuccess(
              'Docker images updated',
              `The tool name changed from '${this.selectedTool?.name}' to '${tool.name}'.`
            );
          })
        )
        .subscribe();

      this.toolService
        .updateDockerimagesForTool(
          this.selectedTool!.id,
          this.form.controls.dockerimages.value as ToolDockerimages
        )
        .subscribe((_) => {
          this.toastService.showSuccess(
            'Tool created',
            `The Docker images for the tool with id ${
              this.selectedTool!.id
            } were updated.`
          );
        });
    }
  }

  submit(): void {
    if (this.existing) {
      this.update();
    } else {
      this.create();
    }
  }
}
